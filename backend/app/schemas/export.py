from pydantic import BaseModel, Field
from typing import List, Optional
from backend.app.schemas.slide import SlideContent


class ExportRequest(BaseModel):
    session_id: str
    presentation_title: str
    slides: Optional[List[SlideContent]] = None
    format: str = Field(default="pptx", description="Export format: pptx | pdf")
    theme: Optional[str] = Field(
        default="midnight_executive",
        description="Color theme: midnight_executive | forest_moss | coral_energy | charcoal_minimal",
    )


class ExportResponse(BaseModel):
    session_id: str
    filename: str
    format: str
    download_url: str
    file_size_bytes: int
