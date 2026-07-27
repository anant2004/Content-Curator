from pydantic import BaseModel, Field
from typing import Optional, List


class UploadResponse(BaseModel):
    session_id: str = Field(..., description="Unique session ID for this upload")
    filename: str
    mime_type: str
    char_count: int
    preview: str = Field(..., description="First 300 chars of extracted text")
    message: str = "File ingested successfully"


class UploadBatchResponse(BaseModel):
    session_id: str = Field(..., description="Unified session ID for the batch")
    filenames: List[str] = Field(..., description="Names of all successfully ingested files")
    failed_filenames: List[str] = Field(default_factory=list, description="Files that could not be ingested")
    total_char_count: int
    preview: str = Field(..., description="First 300 chars of the merged extracted text")
    message: str = "Batch ingested successfully"


class ExtractedContent(BaseModel):
    session_id: str
    raw_text: str
    source_filename: Optional[str] = None
    mime_type: Optional[str] = None


class PasteRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Raw email or plain text to ingest")
    label: Optional[str] = Field(default=None, description="Optional label for this content")

