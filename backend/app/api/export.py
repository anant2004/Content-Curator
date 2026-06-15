import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from backend.app.schemas.export import ExportRequest, ExportResponse
from backend.app.services.generation.pptx_builder import build_pptx
from backend.app.services.generation.pdf_builder import build_pdf
from backend.app.api.generation import get_presentation_store
from backend.app.utils.logger import logger

router = APIRouter(prefix="/export", tags=["Export"])


@router.post("/", response_model=ExportResponse)
async def export_presentation(
    req: ExportRequest,
    pres_store=Depends(get_presentation_store),
):
    """Export slides as PPTX or PDF and return download metadata."""
    # Allow caller to pass their own slides, or fall back to stored ones
    slides = req.slides
    if not slides:
        pres = pres_store.get(req.session_id)
        if not pres:
            raise HTTPException(404, f"Session {req.session_id} not found.")
        slides = pres.slides

    try:
        if req.format == "pdf":
            out_path = build_pdf(slides, req.presentation_title, req.theme or "midnight_executive")
        else:
            out_path = build_pptx(slides, req.presentation_title, req.theme or "midnight_executive")
    except Exception as e:
        logger.exception("Export failed")
        raise HTTPException(500, f"Export failed: {e}")

    file_size = out_path.stat().st_size
    filename = out_path.name
    download_url = f"/export/download/{filename}"

    logger.info(f"Exported session={req.session_id} format={req.format} size={file_size}")

    return ExportResponse(
        session_id=req.session_id,
        filename=filename,
        format=req.format,
        download_url=download_url,
        file_size_bytes=file_size,
    )


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Serve an exported file for download."""
    from backend.app.config import settings
    file_path = Path(settings.temp_dir) / filename

    if not file_path.exists():
        raise HTTPException(404, "File not found or expired.")

    suffix = file_path.suffix.lower()
    media_types = {
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".pdf": "application/pdf",
        ".html": "text/html",
    }
    media_type = media_types.get(suffix, "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename,
    )
