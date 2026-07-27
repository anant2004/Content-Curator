from typing import List, Optional
from backend.app.services.llm.client import llm_client
from backend.app.services.llm.prompts import OUTLINE_SYSTEM, OUTLINE_USER
from backend.app.schemas.generation import OutlineResponse, OutlineItem
from backend.app.utils.logger import logger


MAX_CONTENT_CHARS = 6000  # Trim content to stay within context window


def _build_context_block(
    domain: Optional[str] = None,
    division: Optional[str] = None,
    output_type: Optional[str] = None,
    compliance_frameworks: Optional[List[str]] = None,
    preferred_file_type: Optional[str] = None,
) -> str:
    """Build a formatted context block string for the LLM prompt.

    Returns an empty string if no context fields are provided, so the
    prompt template handles absence cleanly.
    """
    lines = []
    if domain:
        lines.append(f"Domain: {domain}")
    if division:
        lines.append(f"Division: {division}")
    if output_type:
        lines.append(f"Output type: {output_type}")
    if preferred_file_type:
        lines.append(f"Preferred file type/format: {preferred_file_type}")
    if compliance_frameworks:
        lines.append(f"Compliance requirements: {', '.join(compliance_frameworks)}")

    if not lines:
        return ""
    return "\nOrganisational context (align your outline to these):\n" + "\n".join(lines) + "\n"


async def generate_outline(
    content: str,
    num_slides: int = 8,
    audience: str = "general",
    tone: str = "professional",
    focus: str = "key insights",
    user_prompt: str = "",
    session_id: str = "",
    domain: Optional[str] = None,
    division: Optional[str] = None,
    output_type: Optional[str] = None,
    compliance_frameworks: Optional[List[str]] = None,
    preferred_file_type: Optional[str] = None,
) -> OutlineResponse:
    """Generate a structured slide outline from source content."""

    # Trim content to avoid exceeding context window
    trimmed = content[:MAX_CONTENT_CHARS]
    if len(content) > MAX_CONTENT_CHARS:
        logger.info(f"Content trimmed from {len(content)} to {MAX_CONTENT_CHARS} chars")

    # Fallback if user didn't type a prompt
    effective_prompt = user_prompt.strip() if user_prompt and user_prompt.strip() else \
        "Summarise the source document into a clear, professional presentation."

    context_block = _build_context_block(domain, division, output_type, compliance_frameworks, preferred_file_type)


    user_msg = OUTLINE_USER.format_map({
        "num_slides": num_slides,
        "audience": audience or "general audience",
        "tone": tone or "professional",
        "focus": focus or "key insights and findings",
        "user_prompt": effective_prompt,
        "content": trimmed,
        "context_block": context_block,
    })

    for attempt in range(1, 3):  # try up to 2 times
        data = await llm_client.chat_json(
            system_prompt=OUTLINE_SYSTEM,
            user_prompt=user_msg,
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

