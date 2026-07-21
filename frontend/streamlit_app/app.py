"""
Content Curator - Streamlit Main Entry Point

Thin entry point that orchestrates all components.
~50 lines as specified.
"""

import sys
from pathlib import Path

# Ensure `frontend/` is on sys.path so `streamlit_app` package imports work
# when running: streamlit run frontend/streamlit_app/app.py
_FRONTEND_ROOT = Path(__file__).resolve().parent.parent
if str(_FRONTEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_FRONTEND_ROOT))

import streamlit as st
from streamlit_app import state
from streamlit_app.components import (
    render_sidebar,
    render_prompt_bar,
    render_preview_panel,
    render_export_bar,
)
from streamlit_app.styles import style_app


def main():
    """Main app entry point."""
    
    # Page configuration
    st.set_page_config(
        page_title="Content Curator",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    state.init_session_state()
    
    # Load custom styles
    style_app()
    
    # Header with title
    st.markdown("<h2 style='text-align: center;'>📝 TATA STEEL Content Curator</h2>", unsafe_allow_html=True)
    
    st.divider()
    
    # Sidebar (render_sidebar manages its own st.sidebar context)
    render_sidebar()
    
    # Main content area
    col_generate, col_preview = st.columns([1, 1], gap="large")
    
    with col_generate:
        render_prompt_bar()
    
    with col_preview:
        render_preview_panel()
        st.divider()
        render_export_bar()


if __name__ == "__main__":
    main()
