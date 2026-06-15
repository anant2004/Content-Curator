"""
Preview Component

Renders content preview panel with:
- Asset type switcher
- Artifact viewer delegation
- Navigation within artifact
"""

import streamlit as st
from streamlit_app import state


def render_preview_panel():
    """Render the preview panel component."""
    st.markdown("### 👁️ Preview")

    active_asset = state.get_active_asset()

    if not active_asset["type"] or not active_asset["data"]:
        st.info("Select or generate content to preview here")
        return

    asset_type = active_asset["type"]
    asset_data = active_asset["data"]

    # ── Live slides from backend ───────────────────────────────────
    if asset_type == "presentation":
        live_slides = state.get_generated_slides()
        title = state.get_presentation_title() or asset_data.get("title", "Presentation")

        if live_slides:
            st.markdown(f"**{title}**")
            _render_slides_preview(live_slides)
            return

    # ── Fallback: mock / other asset types ────────────────────────
    _render_artifact_viewer(asset_type, asset_data)


def _render_slides_preview(slides: list):
    """
    Render a list of SlideContent dicts from the backend as a simple preview.

    Args:
        slides: List of SlideContent dicts from /api/v1/generate/slides
    """
    if not slides:
        st.info("No slides to preview.")
        return

    total = len(slides)
    slide_num = st.number_input(
        f"Slide (1 – {total})",
        min_value=1,
        max_value=total,
        value=1,
        step=1,
        key="slide_navigator",
    )

    slide = slides[slide_num - 1]

    st.markdown(
        f"""
        <div style="border: 1px solid #DCE3EC; border-radius: 10px;
                    padding: 20px; background: #F9FAFB; min-height: 220px;">
            <h4 style="color: #003B7A; margin-bottom: 12px;">
                Slide {slide_num}/{total} — {slide.get('title', '')}
            </h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    bullets = slide.get("bullets", [])
    if bullets:
        for bullet in bullets:
            st.markdown(f"- {bullet}")
    else:
        st.caption("(no bullet points)")

    notes = slide.get("speaker_notes")
    if notes:
        with st.expander("🎤 Speaker notes"):
            st.caption(notes)




def _render_artifact_viewer(artifact_type: str, artifact_data: dict):
    """
    Delegate to appropriate artifact viewer.
    
    Args:
        artifact_type: Type of artifact (presentation, document, etc.)
        artifact_data: Artifact data
    """
    if artifact_type == "presentation":
        from streamlit_app.components.artifacts.presentation import render_presentation
        render_presentation(artifact_data)
    
    elif artifact_type == "document":
        from streamlit_app.components.artifacts.document import render_document
        render_document(artifact_data)
    
    elif artifact_type == "sop":
        from streamlit_app.components.artifacts.sop import render_sop
        render_sop(artifact_data)
    
    elif artifact_type == "handbook":
        from streamlit_app.components.artifacts.handbook import render_handbook
        render_handbook(artifact_data)
    
    elif artifact_type == "spreadsheet":
        from streamlit_app.components.artifacts.spreadsheet import render_spreadsheet
        render_spreadsheet(artifact_data)
    
    elif artifact_type == "video":
        from streamlit_app.components.artifacts.video import render_video
        render_video(artifact_data)
    
    elif artifact_type == "podcast":
        from streamlit_app.components.artifacts.podcast import render_podcast
        render_podcast(artifact_data)
    
    else:
        st.warning(f"Unknown artifact type: {artifact_type}")
