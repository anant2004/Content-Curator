from pydantic import BaseModel, Field
from typing import List, Optional


class SlideElement(BaseModel):
    type: str
    content: str

    x: int = 10
    y: int = 10

    width: int = 80
    height: int = 20

    font_size: int = 18

    bold: bool = False

    alignment: str = "left"


class SlideContent(BaseModel):
    slide_number: int
    title: str

    bullets: List[str] = Field(default_factory=list)

    speaker_notes: Optional[str] = None

    layout: Optional[str] = Field(
        default="bullets",
        description="bullets | two_column | big_stat | image_text | title_only",
    )

    elements: List[SlideElement] = []

    visual_suggestion: Optional[str] = None

    # LLM design instructions
    title_size: Optional[int] = 28
    body_size: Optional[int] = 18
    alignment: Optional[str] = "left"
    background_style: Optional[str] = "light"
    accent: Optional[str] = None

    # Generation status — set to True if LLM failed to generate this slide
    failed: bool = False
    error_message: Optional[str] = None


class SlideUpdateRequest(BaseModel):
    session_id: str
    slide_number: int
    instruction: str = Field(
        ..., description="Natural language instruction for what to change"
    )
    current_slide: SlideContent


class SlideRegenerateRequest(BaseModel):
    session_id: str
    slide_number: int
    context: Optional[str] = Field(
        default=None, description="Additional context for regeneration"
    )
