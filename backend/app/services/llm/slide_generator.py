import json
import asyncio
from typing import List, Optional

from backend.app.services.llm.client import llm_client
from backend.app.services.llm.prompts import (
    SLIDE_SYSTEM,
    SLIDE_USER,
    SLIDE_EDIT_SYSTEM,
    SLIDE_EDIT_USER,
)
from backend.app.schemas.slide import SlideContent
from backend.app.schemas.generation import OutlineItem
from backend.app.utils.logger import logger
from backend.app.services.llm.outline_generator import _build_context_block

INTER_SLIDE_DELAY = 2.0  # seconds between requests — reduces rate limit pressure


async def _generate_single_slide(
    outline_item: OutlineItem,
    presentation_title: str,
    audience: str,
    tone: str,
    source_excerpt: str,
    user_prompt: str = "",
    context_block: str = "",
) -> SlideContent:
    user_msg = SLIDE_USER.format_map({
        "presentation_title": presentation_title,
        "audience": audience,
        "tone": tone,
        "user_prompt": user_prompt or "Create a professional presentation from the source material.",
        "context_block": context_block,
        "slide_number": outline_item.slide_number,
        "title": outline_item.title,
        "purpose": outline_item.purpose,
        "key_points": ", ".join(outline_item.key_points),
        "source_excerpt": source_excerpt[:1500],
    })
    data = await llm_client.chat_json(
        system_prompt=SLIDE_SYSTEM,
        user_prompt=user_msg,
        max_tokens=3000,
        temperature=0.4,
    )

    slide = SlideContent(**data)

    # Fix 1: Never trust the LLM for slide_number — always force the correct value
    slide.slide_number = outline_item.slide_number

    # Fix 2 & 4: Back-fill bullets from elements[] so pdf_builder has content.
    # Skip image elements (fake filenames) and the title element itself.
    if not slide.bullets and slide.elements:
        slide.bullets = [
            e.content
            for e in slide.elements
            if e.type == "text" and e.content.strip() != slide.title.strip()
        ][:5]

    logger.info(f"""
    Generated Slide {slide.slide_number}
    Title: {slide.title}
    Layout: {slide.layout}
    Bullets: {len(slide.bullets)}
    Visual: {slide.visual_suggestion}
    """)

    return slide


async def generate_slides(
    outline_items: List[OutlineItem],
    presentation_title: str,
    source_content: str,
    audience: str = "general",
    tone: str = "professional",
    user_prompt: str = "",
    domain: Optional[str] = None,
    division: Optional[str] = None,
    output_type: Optional[str] = None,
    compliance_frameworks: Optional[List[str]] = None,
) -> List[SlideContent]:
    """Generate all slide contents sequentially with a two-pass retry strategy.

    1. First pass: attempt every slide with a small delay between requests.
    2. Retry pass: any slide that failed gets one more attempt.
    3. Slides that fail both passes are returned with failed=True.
    """
    excerpt = source_content[:4000]
    context_block = _build_context_block(domain, division, output_type, compliance_frameworks)

    def _placeholder(item: OutlineItem, error: str) -> SlideContent:
        return SlideContent(
            slide_number=item.slide_number,
            title=item.title,
            bullets=item.key_points[:5],
            speaker_notes="",
            layout="bullets",
            visual_suggestion=None,
            failed=True,
            error_message=str(error),
        )

    # ── First pass ────────────────────────────────────────────────
    slides: list[SlideContent] = []
    failed_items: list[OutlineItem] = []

    for i, item in enumerate(outline_items):
        if i > 0:
            logger.debug(f"Waiting {INTER_SLIDE_DELAY}s before slide {item.slide_number}")
            await asyncio.sleep(INTER_SLIDE_DELAY)
        try:
            slide = await _generate_single_slide(
                item, presentation_title, audience, tone, excerpt, user_prompt, context_block
            )
            slides.append(slide)
        except Exception as e:
            logger.warning(f"Slide {item.slide_number} failed on first pass: {e} — will retry")
            slides.append(_placeholder(item, e))
            failed_items.append(item)

    # ── Retry pass ────────────────────────────────────────────────
    if failed_items:
        logger.info(
            f"Retrying {len(failed_items)} failed slide(s): "
            f"{[i.slide_number for i in failed_items]}"
        )
        for item in failed_items:
            await asyncio.sleep(INTER_SLIDE_DELAY)
            try:
                slide = await _generate_single_slide(
                    item, presentation_title, audience, tone, excerpt, user_prompt, context_block
                )
                for idx, s in enumerate(slides):
                    if s.slide_number == item.slide_number:
                        slides[idx] = slide
                        break
                logger.info(f"Slide {item.slide_number} recovered on retry ✓")
            except Exception as e:
                logger.error(
                    f"Slide {item.slide_number} failed again on retry: {e} — "
                    f"keeping as failed placeholder"
                )

    failed_count = sum(1 for s in slides if s.failed)
    if failed_count:
        logger.warning(f"{failed_count} slide(s) could not be generated after retry.")

    return sorted(slides, key=lambda s: s.slide_number)


async def edit_slide(
    current_slide: SlideContent,
    instruction: str,
) -> SlideContent:
    """Edit a single slide based on a natural language instruction."""
    user_prompt = SLIDE_EDIT_USER.format_map({
        "instruction": instruction,
        "current_slide_json": json.dumps(current_slide.model_dump(), indent=2),
        "slide_number": current_slide.slide_number,
    })
    data = await llm_client.chat_json(
        system_prompt=SLIDE_EDIT_SYSTEM,
        user_prompt=user_prompt,
        max_tokens=1200,
        temperature=0.3
    )
    return SlideContent(**data)
