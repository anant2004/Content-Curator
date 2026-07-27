from pydantic import BaseModel, Field
from typing import List, Optional
from backend.app.schemas.slide import SlideContent


class GenerationRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from ingestion step")
    num_slides: int = Field(default=8, ge=1, le=100, description="Target number of slides (1–100)")
    audience: Optional[str] = Field(default=None, description="Target audience (e.g. executives, students)")
    tone: Optional[str] = Field(default="professional", description="Tone: professional, casual, academic")
    focus: Optional[str] = Field(default=None, description="Specific angle or focus area")
    user_prompt: Optional[str] = Field(default=None, description="The user's natural language instruction for the presentation")
    # ── Sidebar metadata forwarded from the frontend ──────────────────────────
    domain: Optional[str] = Field(default=None, description="Content domain, e.g. HSE, Finance, Operations")
    division: Optional[str] = Field(default=None, description="Organisational division, e.g. Steel, Motors")
    output_type: Optional[str] = Field(default=None, description="Desired output artifact type, e.g. Presentation, SOP, Handbook")
    preferred_file_type: Optional[str] = Field(default=None, description="Preferred file type, e.g. PPTX, PDF, DOCX")
    compliance_frameworks: Optional[List[str]] = Field(
        default=None,
        description="Applicable compliance frameworks, e.g. ['ISO 45001', 'OHSAS 18001']",
    )



class OutlineItem(BaseModel):
    slide_number: int
    title: str
    purpose: str = Field(..., description="What this slide accomplishes")
    key_points: List[str]


class OutlineResponse(BaseModel):
    session_id: str
    title: str = Field(..., description="Suggested presentation title")
    outline: List[OutlineItem]
    total_slides: int


class GenerationResponse(BaseModel):
    session_id: str
    presentation_title: str
    slides: List[SlideContent]
    total_slides: int
