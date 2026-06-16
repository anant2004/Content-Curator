from pydantic import BaseModel, Field
from typing import List, Optional
from backend.app.schemas.slide import SlideContent


class GenerationRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from ingestion step")
    num_slides: int = Field(default=8, ge=3, le=20, description="Target number of slides")
    audience: Optional[str] = Field(default=None, description="Target audience (e.g. executives, students)")
    tone: Optional[str] = Field(default="professional", description="Tone: professional, casual, academic")
    focus: Optional[str] = Field(default=None, description="Specific angle or focus area")
    user_prompt: Optional[str] = Field(default=None, description="The user's natural language instruction for the presentation")


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
