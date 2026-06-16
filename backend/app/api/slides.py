from fastapi import APIRouter, HTTPException, Depends

from backend.app.schemas.slide import SlideContent, SlideUpdateRequest, SlideRegenerateRequest
from backend.app.services.llm.slide_generator import edit_slide
from backend.app.api.generation import get_presentation_store
from backend.app.services.generation.presentation_store import presentation_store
from backend.app.utils.logger import logger

router = APIRouter(prefix="/slides", tags=["Slides"])


@router.patch("/edit", response_model=SlideContent)
async def edit_slide_endpoint(
    req: SlideUpdateRequest,
    pres_store: dict = Depends(get_presentation_store),
):
    """Edit a single slide using a natural language instruction."""
    pres = pres_store.get(req.session_id)
    if not pres:
        raise HTTPException(404, f"Session {req.session_id} not found.")

    try:
        updated = await edit_slide(
            current_slide=req.current_slide,
            instruction=req.instruction,
        )
    except Exception as e:
        logger.exception("Slide edit failed")
        raise HTTPException(500, f"Slide edit failed: {e}")

    # Update in store and persist to disk
    for i, s in enumerate(pres.slides):
        if s.slide_number == req.slide_number:
            pres.slides[i] = updated
            break

    presentation_store.set(req.session_id, pres)
    return updated


@router.put("/{session_id}/{slide_number}", response_model=SlideContent)
async def update_slide_content(
    session_id: str,
    slide_number: int,
    slide: SlideContent,
    pres_store: dict = Depends(get_presentation_store),
):
    """Directly replace a slide's content (manual edit from frontend)."""
    pres = pres_store.get(session_id)
    if not pres:
        raise HTTPException(404, f"Session {session_id} not found.")

    for i, s in enumerate(pres.slides):
        if s.slide_number == slide_number:
            pres.slides[i] = slide
            presentation_store.set(session_id, pres)  # persist to disk
            return slide

    raise HTTPException(404, f"Slide {slide_number} not found in session {session_id}.")


@router.get("/{session_id}/{slide_number}", response_model=SlideContent)
async def get_slide(
    session_id: str,
    slide_number: int,
    pres_store: dict = Depends(get_presentation_store),
):
    """Get a single slide by session and slide number."""
    pres = pres_store.get(session_id)
    if not pres:
        raise HTTPException(404, f"Session {session_id} not found.")

    for s in pres.slides:
        if s.slide_number == slide_number:
            return s

    raise HTTPException(404, f"Slide {slide_number} not found.")
