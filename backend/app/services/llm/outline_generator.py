from typing import List
from backend.app.services.llm.client import llm_client
from backend.app.services.llm.prompts import OUTLINE_SYSTEM, OUTLINE_USER
from backend.app.schemas.generation import OutlineResponse, OutlineItem
from backend.app.utils.logger import logger
from string import Template

MAX_CONTENT_CHARS = 6000  # Trim content to stay within context window


async def generate_outline(
    content: str,
    num_slides: int = 8,
    audience: str = "general",
    tone: str = "professional",
    focus: str = "key insights",
    session_id: str = "",
) -> OutlineResponse:
    """Generate a structured slide outline from source content."""

    # Trim content to avoid exceeding context window
    trimmed = content[:MAX_CONTENT_CHARS]
    if len(content) > MAX_CONTENT_CHARS:
        logger.info(f"Content trimmed from {len(content)} to {MAX_CONTENT_CHARS} chars")

    user_prompt = Template(OUTLINE_USER).substitute(
        num_slides=num_slides,
        audience=audience or "general audience",
        tone=tone or "professional",
        focus=focus or "key insights and findings",
        content=trimmed,
    )

    for attempt in range(1, 3):  # try up to 2 times
        data = await llm_client.chat_json(
            system_prompt=OUTLINE_SYSTEM,
            user_prompt=user_prompt,
            max_tokens=4000,
            temperature=0.5,
        )

        outline_items = [OutlineItem(**item) for item in data.get("outline", [])]

        if len(outline_items) == num_slides:
            break  # LLM returned the correct count — done

        logger.warning(
            f"Attempt {attempt}: LLM returned {len(outline_items)} outline items "
            f"but exactly {num_slides} were requested."
            + (" Retrying..." if attempt < 2 else " Using what we got.")
        )

    # Re-number sequentially (LLM sometimes misnumbers after retries)
    for i, item in enumerate(outline_items, start=1):
        item.slide_number = i

    # Last resort: truncate only if retry still gave wrong count
    if len(outline_items) > num_slides:
        logger.warning(f"Truncating {len(outline_items)} → {num_slides} slides after retry.")
        outline_items = outline_items[:num_slides]

    return OutlineResponse(
        session_id=session_id,
        title=data.get("title", "Untitled Presentation"),
        outline=outline_items,
        total_slides=len(outline_items),
    )
