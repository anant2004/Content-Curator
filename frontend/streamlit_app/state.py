"""
Streamlit Session State Management

Handles all session_state initialization and helper functions
for maintaining global state across app reruns.
"""

import streamlit as st
from datetime import datetime
from typing import Optional


def init_session_state():
    """Initialize all session state variables."""
    
    # Chat & Generation
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_prompt" not in st.session_state:
        st.session_state.current_prompt = ""
    
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False
    
    # Document Management
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    
    if "selected_domain" not in st.session_state:
        st.session_state.selected_domain = None
    
    if "selected_division" not in st.session_state:
        st.session_state.selected_division = None
    
    if "selected_output_type" not in st.session_state:
        st.session_state.selected_output_type = None
    
    if "selected_file_type" not in st.session_state:
        st.session_state.selected_file_type = "PDF"
    
    # Generated Assets
    if "generated_assets" not in st.session_state:
        st.session_state.generated_assets = {}
    
    if "active_asset_type" not in st.session_state:
        st.session_state.active_asset_type = None
    
    if "active_asset_data" not in st.session_state:
        st.session_state.active_asset_data = None
    
    # Refinements & Improvements
    if "applied_improvements" not in st.session_state:
        st.session_state.applied_improvements = []
    
    if "improvement_pending" not in st.session_state:
        st.session_state.improvement_pending = False
    
    # UI State
    if "show_advanced_options" not in st.session_state:
        st.session_state.show_advanced_options = False
    
    if "selected_compliance_frameworks" not in st.session_state:
        st.session_state.selected_compliance_frameworks = []
    
    if "uploaded_template" not in st.session_state:
        st.session_state.uploaded_template = None
    
    if "selected_sample_template" not in st.session_state:
        st.session_state.selected_sample_template = None

    # ── Backend integration state ─────────────────────────────────────

    # session_id is returned by the ingest step and passed to generate/export
    if "session_id" not in st.session_state:
        st.session_state.session_id = None

    # Raw slides list returned by POST /api/v1/generate/slides
    if "generated_slides" not in st.session_state:
        st.session_state.generated_slides = []

    # presentation_title from the generation response
    if "presentation_title" not in st.session_state:
        st.session_state.presentation_title = ""

    # Short text preview shown after a successful ingest
    if "ingested_preview" not in st.session_state:
        st.session_state.ingested_preview = ""

    # Whether the live backend is reachable
    if "backend_available" not in st.session_state:
        st.session_state.backend_available = False

    # Toggle: when True the frontend uses mock data instead of calling the backend
    if "use_mock_data" not in st.session_state:
        st.session_state.use_mock_data = False


def get_chat_history():
    """Retrieve chat history."""
    return st.session_state.get("chat_history", [])


def add_to_chat_history(role: str, content: str):
    """Add message to chat history."""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })


def clear_chat_history():
    """Clear all chat history."""
    st.session_state.chat_history = []


def set_generating(status: bool):
    """Set generation status."""
    st.session_state.is_generating = status


def is_generating():
    """Check if generation is in progress."""
    return st.session_state.get("is_generating", False)


def set_active_asset(asset_type: str, asset_data: dict):
    """Set the currently active asset for preview."""
    st.session_state.active_asset_type = asset_type
    st.session_state.active_asset_data = asset_data


def get_active_asset():
    """Get the currently active asset."""
    return {
        "type": st.session_state.get("active_asset_type"),
        "data": st.session_state.get("active_asset_data")
    }


def add_improvement(improvement_id: str, improvement_text: str):
    """Add an improvement request."""
    st.session_state.applied_improvements.append({
        "id": improvement_id,
        "text": improvement_text,
        "timestamp": datetime.now().isoformat()
    })


def get_applied_improvements():
    """Get all applied improvements."""
    return st.session_state.get("applied_improvements", [])


# ── Backend integration helpers ───────────────────────────────────────


def set_session_id(session_id: str):
    """Store the session_id returned by the ingest step."""
    st.session_state.session_id = session_id


def get_session_id() -> Optional[str]:
    """Retrieve the current ingest session_id."""
    return st.session_state.get("session_id")


def set_generated_slides(slides: list, title: str = ""):
    """Store slides returned by the generate step."""
    st.session_state.generated_slides = slides
    st.session_state.presentation_title = title


def get_generated_slides() -> list:
    """Return the current list of generated slides."""
    return st.session_state.get("generated_slides", [])


def get_presentation_title() -> str:
    """Return the presentation title from the last generation."""
    return st.session_state.get("presentation_title", "")


def set_backend_status(available: bool):
    """Update the cached backend availability flag."""
    st.session_state.backend_available = available


def is_backend_available() -> bool:
    """Return whether the last health check succeeded."""
    return st.session_state.get("backend_available", False)


def is_mock_mode() -> bool:
    """Return True when the user has enabled mock-data mode."""
    return st.session_state.get("use_mock_data", False)
