from fastapi import APIRouter, HTTPException, Depends

from backend.app.schemas.generation import (
    GenerationRequest,
    OutlineResponse,
    GenerationResponse,
)
from backend.app.services.llm.outline_generator import generate_outline
from backend.app.services.llm.slide_generator import generate_slides
from backend.app.services.ingestion.session_store import session_store
from backend.app.services.generation.presentation_store import presentation_store
from backend.app.utils.logger import logger

router = APIRouter(prefix="/generate", tags=["Generation"])


def get_presentation_store():
    """Return the file-backed presentation store (used by export & slides routes)."""
    return presentation_store


@router.post("/outline", response_model=OutlineResponse)
async def create_outline(
    req: GenerationRequest,
):
    """Generate a slide outline from ingested content."""
    content_obj = session_store.get(req.session_id)
    if not content_obj:
        raise HTTPException(404, f"Session {req.session_id} not found. Ingest content first.")

    try:
        outline = await generate_outline(
            content=content_obj.raw_text,
            num_slides=req.num_slides,
            audience=req.audience or "general audience",
            tone=req.tone or "professional",
            focus=req.focus or "key insights",
            session_id=req.session_id,
        )
    except Exception as e:
        logger.exception("Outline generation failed")
        raise HTTPException(500, f"Outline generation failed: {e}")

    return outline


@router.post("/slides", response_model=GenerationResponse)
async def create_slides(
    req: GenerationRequest,
):
    """Generate full slide content (outline + per-slide) from ingested content."""
    content_obj = session_store.get(req.session_id)
    if not content_obj:
        raise HTTPException(404, f"Session {req.session_id} not found. Ingest content first.")

    try:
        outline = await generate_outline(
            content=content_obj.raw_text,
            num_slides=req.num_slides,
            audience=req.audience or "general audience",
            tone=req.tone or "professional",
            focus=req.focus or "key insights",
            session_id=req.session_id,
        )
        slides = await generate_slides(
            outline_items=outline.outline,
            presentation_title=outline.title,
            source_content=content_obj.raw_text,
            audience=req.audience or "general audience",
            tone=req.tone or "professional",
        )
    except Exception as e:
        logger.exception("Slide generation failed")
        raise HTTPException(500, f"Slide generation failed: {e}")

    result = GenerationResponse(
        session_id=req.session_id,
        presentation_title=outline.title,
        slides=slides,
        total_slides=len(slides),
    )
    presentation_store.set(req.session_id, result)
    logger.info(f"Generated {len(slides)} slides for session={req.session_id} — saved to presentations.json")
    return result


@router.get("/slides/{session_id}", response_model=GenerationResponse)
async def get_slides(
    session_id: str,
):
    """Retrieve previously generated slides (reads from presentations.json)."""
    result = presentation_store.get(session_id)
    if not result:
        raise HTTPException(404, f"No slides found for session {session_id}.")
    return result


@router.delete("/slides/{session_id}", status_code=204)
async def delete_slides(session_id: str):
    """Delete stored slides for a session from presentations.json."""
    presentation_store.delete(session_id)
    logger.info(f"Deleted slides for session={session_id} from presentations.json")
