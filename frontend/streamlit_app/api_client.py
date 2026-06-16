"""
API Client Module

Handles all HTTP communication with the backend FastAPI service.
Provides a single interface for all backend API calls.

Backend base URL: http://localhost:8000
All API routes are prefixed with /api/v1/
"""

import requests
import streamlit as st
from typing import Optional, Dict, Any, List
from io import BytesIO


BASE_API = "/api/v1"


class APIClient:
    """Client for backend API communication."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.

        Args:
            base_url: Backend API base URL (no trailing slash)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = 300  # LLM calls can be slow

    # ── Internal helpers ─────────────────────────────────────────────

    def _url(self, path: str) -> str:
        """Build full URL from a path."""
        return f"{self.base_url}{path}"

    def _get(self, path: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request and return JSON."""
        try:
            r = requests.get(self._url(path), timeout=self.timeout, **kwargs)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request with a JSON body and return JSON."""
        try:
            r = requests.post(
                self._url(path),
                json=payload,
                timeout=self.timeout,
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _post_multipart(self, path: str, files: Dict, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request with multipart/form-data and return JSON."""
        try:
            r = requests.post(
                self._url(path),
                files=files,
                data=data or {},
                timeout=self.timeout,
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _get_bytes(self, path: str) -> Optional[bytes]:
        """Make a GET request and return raw bytes (for file downloads)."""
        try:
            r = requests.get(self._url(path), timeout=self.timeout)
            r.raise_for_status()
            return r.content
        except requests.exceptions.RequestException as e:
            return None

    # ── Health Check ─────────────────────────────────────────────────

    def health_check(self) -> bool:
        """
        Check if the backend is available.

        Backend endpoint: GET /health
        Returns True when backend responds with {"status": "healthy"}
        """
        try:
            response = self._get("/health")
            return response.get("status") == "healthy"
        except Exception:
            return False

    # ── Ingestion ────────────────────────────────────────────────────

    def ingest_file(self, uploaded_file) -> Dict[str, Any]:
        """
        Upload a file (Streamlit UploadedFile) to the backend for ingestion.

        Backend endpoint: POST /api/v1/ingest/upload
        Returns: {session_id, filename, mime_type, char_count, preview}

        Args:
            uploaded_file: A Streamlit UploadedFile object
        """
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type or "application/octet-stream",
            )
        }
        return self._post_multipart(f"{BASE_API}/ingest/upload", files=files)

    def ingest_text(self, text: str, label: Optional[str] = None) -> Dict[str, Any]:
        """
        Paste plain text into the backend for ingestion (no file needed).

        Backend endpoint: POST /api/v1/ingest/paste
        Returns: {session_id, filename, mime_type, char_count, preview}

        Args:
            text:  The raw text to ingest (user prompt or pasted document)
            label: Optional display name for the text source
        """
        payload = {
            "text": text,
            "label": label or "pasted_text",
        }
        return self._post_json(f"{BASE_API}/ingest/paste", payload)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve an existing ingestion session.

        Backend endpoint: GET /api/v1/ingest/session/{session_id}
        """
        return self._get(f"{BASE_API}/ingest/session/{session_id}")

    # ── Generation ───────────────────────────────────────────────────

    def generate_outline(
        self,
        session_id: str,
        num_slides: int = 8,
        audience: Optional[str] = None,
        tone: Optional[str] = "professional",
        focus: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a slide outline from a previously ingested session.

        Backend endpoint: POST /api/v1/generate/outline
        Returns: {session_id, title, outline: [...], total_slides}

        Args:
            session_id: From a prior ingest_file() or ingest_text() call
            num_slides:  Target number of slides (3–20)
            audience:    Target audience description
            tone:        Tone (professional / casual / academic)
            focus:       Specific focus area
            user_prompt: The user's typed instruction (what they want built)
        """
        payload = {
            "session_id": session_id,
            "num_slides": num_slides,
            "audience": audience or "general audience",
            "tone": tone or "professional",
            "focus": focus or "key insights",
            "user_prompt": user_prompt or "",
        }
        return self._post_json(f"{BASE_API}/generate/outline", payload)

    def generate_slides(
        self,
        session_id: str,
        num_slides: int = 8,
        audience: Optional[str] = None,
        tone: Optional[str] = "professional",
        focus: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate full slide content (outline + per-slide details).

        Backend endpoint: POST /api/v1/generate/slides
        Returns: {session_id, presentation_title, slides: [...], total_slides}

        Args:
            session_id: From a prior ingest_file() or ingest_text() call
            num_slides:  Target number of slides (3–20)
            audience:    Target audience description
            tone:        Tone (professional / casual / academic)
            focus:       Specific focus area
            user_prompt: The user's typed instruction (what they want built)
        """
        payload = {
            "session_id": session_id,
            "num_slides": num_slides,
            "audience": audience or "general audience",
            "tone": tone or "professional",
            "focus": focus or "key insights",
            "user_prompt": user_prompt or "",
        }
        return self._post_json(f"{BASE_API}/generate/slides", payload)

    def get_slides(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve previously generated slides for a session.

        Backend endpoint: GET /api/v1/generate/slides/{session_id}
        """
        return self._get(f"{BASE_API}/generate/slides/{session_id}")

    # ── Slide Editing ────────────────────────────────────────────────

    def edit_slide(
        self,
        session_id: str,
        slide_number: int,
        instruction: str,
        current_slide: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Edit a single slide with a natural language instruction.

        Backend endpoint: PATCH /api/v1/slides/edit
        Returns: Updated SlideContent dict
        """
        payload = {
            "session_id": session_id,
            "slide_number": slide_number,
            "instruction": instruction,
            "current_slide": current_slide,
        }
        try:
            r = requests.patch(
                self._url(f"{BASE_API}/slides/edit"),
                json=payload,
                timeout=self.timeout,
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    # ── Export ───────────────────────────────────────────────────────

    def export_presentation(
        self,
        session_id: str,
        presentation_title: str,
        slides: List[Dict[str, Any]],
        format: str = "pptx",
        theme: Optional[str] = "midnight_executive",
    ) -> Optional[bytes]:
        """
        Export slides as PPTX or PDF and return the file bytes.

        Two-step process:
          1. POST /api/v1/export/          → get {download_url, filename, ...}
          2. GET  /api/v1/export/download/{filename} → receive binary file

        Args:
            session_id:           Session ID (from ingest step)
            presentation_title:   Title used in the generated file
            slides:               List of SlideContent dicts
            format:               "pptx" or "pdf"
            theme:                Color theme name

        Returns:
            Raw file bytes, or None on failure
        """
        payload = {
            "session_id": session_id,
            "presentation_title": presentation_title,
            "slides": slides,
            "format": format,
            "theme": theme or "midnight_executive",
        }
        meta = self._post_json(f"{BASE_API}/export/", payload)
        if "error" in meta:
            st.error(f"Export failed: {meta['error']}")
            return None

        download_url = meta.get("download_url")
        if not download_url:
            st.error("Backend did not return a download URL.")
            return None

        # Download the actual binary file
        file_bytes = self._get_bytes(download_url)
        if file_bytes is None:
            st.error("Could not download the exported file from the backend.")
        return file_bytes


# ── Singleton accessor ────────────────────────────────────────────────


@st.cache_resource
def get_api_client() -> APIClient:
    """Get or create the shared API client instance."""
    return APIClient()
