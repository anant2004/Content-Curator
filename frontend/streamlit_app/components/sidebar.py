"""
Sidebar Component

Renders left sidebar with:
- Domain & output type filters
- Session/recent documents
- Suggested actions
"""

import streamlit as st
from streamlit_app.config import (
    DOMAINS,
    DIVISIONS,
    OUTPUT_TYPES,
    FILE_TYPES,
    RECENT_DOCUMENTS,
    SUGGESTED_ACTIONS,
)
from streamlit_app import state
from streamlit_app.api_client import get_api_client


def render_sidebar():
    """Render the sidebar component."""
    with st.sidebar:

        # ── Backend Status ──────────────────────────────────────
        _render_backend_status()

        st.markdown("### ⚙️ Content Configuration")
        # Domain Selector
        st.session_state.selected_domain = st.selectbox(
            "Select Domain",
            DOMAINS,
            key="domain_select",
        )

        # Division Selector
        st.session_state.selected_division = st.selectbox(
            "Select Division",
            DIVISIONS,
            key="division_select",
        )

        # Output Type Selector
        st.session_state.selected_output_type = st.selectbox(
            "Output Type",
            OUTPUT_TYPES,
            key="output_type_select",
        )

        # File Type Selector
        st.session_state.selected_file_type = st.selectbox(
            "Preferred File Type",
            FILE_TYPES,
            key="file_type_select",
        )

        st.divider()

        # Recent Documents Section
        st.markdown(
            '<span class="sidebar-section-title">📄 Recent Documents</span>',
            unsafe_allow_html=True,
        )
        if RECENT_DOCUMENTS:
            for doc in RECENT_DOCUMENTS:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(
                        f'<div class="recent-doc-card">'
                        f'<span class="recent-doc-name">{doc["name"]}</span>'
                        f'<span class="recent-doc-meta">{doc["type"]} · {doc["date"]}</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    if st.button("📂", key=f"doc_{doc['id']}"):
                        state.set_active_asset(doc["type"], doc)
        else:
            st.info("No recent documents")

        st.divider()

        # Suggested Actions
        st.markdown(
            '<span class="sidebar-section-title">💡 Suggested Actions</span>',
            unsafe_allow_html=True,
        )
        for action in SUGGESTED_ACTIONS[:3]:
            if st.button(
                f"➜ {action['label']}",
                key=f"action_{action['label']}",
                use_container_width=True,
            ):
                st.session_state.current_prompt = action["prompt"]
                st.session_state.selected_output_type = action["outputType"]
                st.rerun()
        
        # Advanced Options moved to prompt bar
        st.info("💡 Tip: Advanced options (compliance frameworks, style templates) are in the Generate section below.")


def _render_backend_status():
    """
    Show backend health status and a mock-mode toggle at the top of the sidebar.

    - Runs a health check on every render (cached by @st.cache_resource on the client).
    - Displays 🟢 / 🔴 so the user knows whether the backend is running.
    - Provides a toggle to switch to mock mode when the backend is unavailable.
    """
    api = get_api_client()
    is_live = api.health_check()
    state.set_backend_status(is_live)

    if is_live:
        st.success("🟢 Backend connected — live mode")
    else:
        st.error("🔴 Backend offline")
        st.caption("Start the backend with:\n```\nuvicorn backend.app.main:app --reload\n```")

    # Mock mode toggle
    use_mock = st.toggle(
        "Use mock data (offline mode)",
        value=st.session_state.get("use_mock_data", False),
        key="mock_toggle",
        help="When enabled, the frontend uses built-in mock data instead of calling the backend.",
    )
    st.session_state.use_mock_data = use_mock

    st.divider()

