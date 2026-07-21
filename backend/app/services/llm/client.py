import json
import asyncio
import httpx
from json_repair import repair_json
from typing import Optional
from backend.app.config import settings
from backend.app.utils.logger import logger

# ── Rate-limit retry config ───────────────────────────────────────────────────
_MAX_RETRIES = 5
_BASE_BACKOFF = 5.0  # seconds; doubles each retry: 5 → 10 → 20 → 40 → 80


class OpenRouterClient:
    """Async wrapper around any OpenAI-compatible API (OpenRouter, Gemini, etc.)."""

    def __init__(self):
        self.base_url = settings.openrouter_base_url.rstrip("/")
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://contentcurator.ai",
            "X-Title": "Content Curator",
        }

    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """Send a chat completion request and return the response text."""
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        logger.debug(f"Calling OpenRouter model={self.model}")

        for attempt in range(1, _MAX_RETRIES + 1):
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )

            if response.status_code == 200:
                break  # success — exit retry loop

            if response.status_code in (429, 503):
                if attempt == _MAX_RETRIES:
                    raise RuntimeError(
                        f"LLM API rate limited after {_MAX_RETRIES} retries: "
                        f"{response.text[:200]}"
                    )
                # Honour Retry-After if provided, else use exponential backoff
                retry_after = response.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else _BASE_BACKOFF * (2 ** (attempt - 1))
                logger.warning(
                    f"Rate limited (HTTP {response.status_code}) — "
                    f"attempt {attempt}/{_MAX_RETRIES}, retrying in {wait:.0f}s"
                )
                await asyncio.sleep(wait)
                continue

            # Any other non-200 is a hard failure — don't retry
            logger.error(f"OpenRouter error {response.status_code}: {response.text}")
            raise RuntimeError(
                f"LLM API error {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        print("=================JSON RESPONSE=====================")
        try:
            print(json.dumps(json.loads(content), indent=2))
        except Exception:
            print(content)  # fallback: print raw if not valid JSON
        print("=================JSON RESPONSE END=====================")
        if content is None:
            raise ValueError("LLM returned empty response")
        logger.debug(f"LLM response length: {len(content)} chars")
        return content


    async def chat_json(
    self,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 6000,
    temperature: float = 0.5,
) -> dict:
        raw = await self.chat(system_prompt, user_prompt, max_tokens, temperature)

        if not raw:
            logger.error("LLM returned empty response")
            raise ValueError("LLM returned empty response")

        cleaned = raw.strip()

        try:
        # Remove markdown code fences
            if cleaned.startswith("```"):
                cleaned = cleaned.replace("```json", "")
                cleaned = cleaned.replace("```", "")
                cleaned = cleaned.strip()

            # Find JSON boundaries
            start = cleaned.find("{")
            end = cleaned.rfind("}")

            if start == -1 or end == -1:
                logger.error(f"No JSON object found in LLM response:\n{raw[:500]}")
                raise ValueError("No JSON object found")

            # Keep only JSON part
            cleaned = cleaned[start : end + 1]

            # Remove common LLM garbage after JSON
            garbage_patterns = [
                "</</</",
                "</",
                "###",
            ]

            for pattern in garbage_patterns:
                cleaned = cleaned.replace(pattern, "")

            cleaned = cleaned.strip()

            return json.loads(cleaned)

        except json.JSONDecodeError as e:
            logger.warning(
                f"Raw JSON parse failed: {e} — attempting json_repair\n"
                f"Cleaned response:\n{cleaned[:500]}"
            )
            try:
                repaired = repair_json(cleaned, return_objects=False)
                result = json.loads(repaired)
                logger.info("json_repair recovered the response successfully")
                return result
            except Exception as repair_err:
                logger.error(
                    f"json_repair also failed: {repair_err}\n"
                    f"Raw response:\n{raw[:1000]}"
                )
                raise ValueError(f"LLM returned invalid JSON: {e}") from e


# Singleton
llm_client = OpenRouterClient()
