"""
Export Bar Component

Renders export section with:
- Export format buttons (PPTX, PDF)
- Download handlers (2-step: POST export → GET binary)
- Refinement / improvement suggestions (local only — no backend refine endpoint yet)
"""

import streamlit as st
from streamlit_app import state
from streamlit_app.api_client import get_api_client
from streamlit_app.config import IMPROVEMENT_SUGGESTIONS


def render_export_bar():
    """Render the export bar component."""
    active_asset = state.get_active_asset()

    if not active_asset["type"] or not active_asset["data"]:
        st.info("Generate content first to export")
        return

    st.markdown("### 📥 Export & Refine")

    asset_data = active_asset["data"]
    slides = state.get_generated_slides()
    title = state.get_presentation_title() or asset_data.get("title", "Presentation")
    session_id = state.get_session_id() or asset_data.get("id", "unknown")

    # ── Export section ──────────────────────────────────────────────
    st.markdown("#### Export Formats")

    # Read sidebar preference to highlight the preferred format
    preferred_ext = state.get_effective_file_type().lower()
    # Normalise: map 'pptx'/'pdf' — anything else defaults to pptx
    preferred_format = "pdf" if "pdf" in preferred_ext else "pptx"

    # Backend only supports PPTX and PDF — show those as primary
    col1, col2 = st.columns(2)

    with col1:
        pptx_type = "primary" if preferred_format == "pptx" else "secondary"
        if st.button("🎯 PowerPoint (.pptx)", use_container_width=True, type=pptx_type):
            _handle_export(session_id, title, slides, "pptx")

    with col2:
        pdf_type = "primary" if preferred_format == "pdf" else "secondary"
        if st.button("📄 PDF", use_container_width=True, type=pdf_type):
            _handle_export(session_id, title, slides, "pdf")

    # Theme selector
    theme = st.selectbox(
        "Slide theme",
        [
            "midnight_executive",
            "forest_moss",
            "coral_energy",
            "charcoal_minimal",
        ],
        key="export_theme",
    )
    # Store theme choice so _handle_export can read it
    st.session_state._export_theme = theme

    # Style template note
    uploaded_template = st.session_state.get("uploaded_template")
    if uploaded_template:
        st.info(
            f"🎨 Style template **'{uploaded_template.name}'** uploaded in sidebar. "
            "Full template-based theming will be applied in a future update."
        )

    st.divider()

    # ── Refinement section (local — no backend endpoint) ────────────
    st.markdown("#### Refine Content")
    st.caption("Improvements are saved locally and sent on the next export.")
    st.markdown("**Suggested Improvements:**")

    for suggestion in IMPROVEMENT_SUGGESTIONS:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(suggestion)
        with col2:
            if st.button("✓", key=f"improve_{suggestion}", use_container_width=True):
                state.add_improvement(
                    improvement_id=suggestion.replace(" ", "_"),
                    improvement_text=suggestion,
                )
                st.success("Improvement noted!")
                st.rerun()

    # Custom refinement
    st.markdown("**Custom Request:**")
    custom_request = st.text_area(
        "Enter custom refinement...",
        placeholder="e.g., Make it more executive-focused...",
        height=60,
        key="custom_refinement",
    )

    if st.button("🔄 Save Refinement", use_container_width=True):
        if custom_request.strip():
            state.add_improvement(
                improvement_id="custom",
                improvement_text=custom_request,
            )
            st.success("Refinement saved — will apply on next generation.")
            st.rerun()
        else:
            st.warning("Please enter a refinement request")


# ── Export handler ──────────────────────────────────────────────────────


def _handle_export(
    session_id: str,
    presentation_title: str,
    slides: list,
    format_type: str,
):
    """
    Export slides via the backend and offer the file as a download.

    Two-step process:
      1. POST /api/v1/export/           → metadata {download_url, filename}
      2. GET  /api/v1/export/download/{filename} → binary bytes

    Args:
        session_id:           Current ingest/generation session
        presentation_title:   Title of the presentation
        slides:               List of SlideContent dicts
        format_type:          "pptx" or "pdf"
    """
    if state.is_mock_mode():
        st.warning("Export is not available in mock mode. Start the backend and disable mock mode.")
        return

    if not slides:
        st.error("No slides to export. Generate content first.")
        return

    theme = st.session_state.get("_export_theme", "midnight_executive")

    try:
        api = get_api_client()

        with st.spinner(f"📦 Building {format_type.upper()} file…"):
            file_bytes = api.export_presentation(
                session_id=session_id,
                presentation_title=presentation_title,
                slides=slides,
                format=format_type,
                theme=theme,
            )

        if file_bytes:
            mime = _get_mime_type(format_type)
            filename = f"{_slugify(presentation_title)}.{format_type}"

            st.download_button(
                label=f"⬇️ Download {format_type.upper()}",
                data=file_bytes,
                file_name=filename,
                mime=mime,
                key=f"dl_{format_type}_{session_id}",
            )
            st.success(f"✓ {format_type.upper()} ready — click the button above to download.")
        else:
            st.error("Export failed — the backend returned no file data.")

    except Exception as e:
        st.error(f"Export error: {e}")


# ── Helpers ─────────────────────────────────────────────────────────────


def _get_mime_type(format_type: str) -> str:
    """Return the MIME type for a given export format."""
    mime_types = {
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "pdf": "application/pdf",
    }
    return mime_types.get(format_type, "application/octet-stream")


def _slugify(text: str) -> str:
    """Convert a title to a safe filename."""
    import re
    return re.sub(r"[^\w\-]", "_", text.lower())[:60]
