"""
Sidebar Component

Renders left sidebar with:
- INPUT SECTION label (always visible)
- Mock mode toggle (with safe fallback)
- Content Configuration
- Select Domain (with conditional custom input)
- Select Division
- Output Type
- Preferred File Type (with conditional custom input)
- Upload Documents
- Advanced Options (Compliance Frameworks & Style Templates)
"""

import streamlit as st
from streamlit_app.config import (
    DOMAINS,
    DIVISIONS,
    OUTPUT_TYPES,
    FILE_TYPES,
    COMPLIANCE_FRAMEWORKS,
)
from streamlit_app import state


def render_sidebar():
    """Render the sidebar component."""
    with st.sidebar:

        # ── CSS: bold the INPUT SECTION expander title ───────────
        st.markdown(
            """
            <style>
            /* Bold the INPUT SECTION expander label specifically */
            details[data-testid="stExpander"] summary p {
                font-weight: 700 !important;
                font-size: 14px !important;
                color: #003B7A !important;
                letter-spacing: 0.04em !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # ── Backend / mock toggle (safe fallback) ────────────────
        try:
            from streamlit_app.api_client import get_api_client
            api = get_api_client()
            is_live = api.health_check()
            state.set_backend_status(is_live)
            status_text = "🟢 Backend connected" if is_live else "🔴 Backend offline"
        except Exception:
            is_live = False
            status_text = "🔴 Backend offline"

        col_tog, col_status = st.columns([1, 1])
        with col_tog:
            use_mock = st.toggle(
                "Mock mode",
                value=st.session_state.get("use_mock_data", not is_live),
                key="mock_toggle",
                help="When enabled, uses built-in mock data instead of calling the backend.",
            )
            st.session_state.use_mock_data = use_mock
        with col_status:
            st.markdown(
                f"<div style='padding-top:8px; font-size:11px; color:#6B7280;'>{status_text}</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Content Configuration ────────────────────────────────
        st.markdown("### ⚙️ Content Configuration")

        # 1. Select Domain
        selected_domain = st.selectbox(
            "Select Domain",
            DOMAINS,
            key="domain_select",
        )
        st.session_state.selected_domain = selected_domain

        if selected_domain == "Others":
            custom_domain = st.text_input(
                "Custom Domain",
                value=st.session_state.get("custom_domain", ""),
                placeholder="Enter custom domain",
                key="custom_domain_input",
                label_visibility="collapsed",
            )
            st.session_state.custom_domain = custom_domain

        # 2. Select Division
        st.session_state.selected_division = st.selectbox(
            "Select Division",
            DIVISIONS,
            key="division_select",
        )

        # 3. Output Type
        st.session_state.selected_output_type = st.selectbox(
            "Output Type",
            OUTPUT_TYPES,
            key="output_type_select",
        )

        # 4. Preferred File Type
        selected_file_type = st.selectbox(
            "Preferred File Type",
            FILE_TYPES,
            key="file_type_select",
        )
        st.session_state.selected_file_type = selected_file_type

        if selected_file_type == "Others":
            custom_file_type = st.text_input(
                "Custom File Type",
                value=st.session_state.get("custom_file_type", ""),
                placeholder="Enter preferred file type",
                key="custom_file_type_input",
                label_visibility="collapsed",
            )
            st.session_state.custom_file_type = custom_file_type

        # 5. Upload Documents
        st.markdown("#### 📎 Upload Documents")
        col_up1, col_up2 = st.columns([4, 1])
        with col_up1:
            uploaded_files = st.file_uploader(
                "Upload Documents (PDF, DOCX, PPTX, EML, TXT)",
                type=["pdf", "docx", "pptx", "eml", "txt"],
                accept_multiple_files=True,
                key="file_uploader",
                label_visibility="collapsed",
            )
        with col_up2:
            if st.button("🗑️", key="clear_sidebar_uploads", use_container_width=True, help="Clear all uploads"):
                st.session_state.uploaded_files = []
                st.session_state.session_id = None
                st.session_state.ingested_preview = ""
                st.rerun()

        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"✓ {len(uploaded_files)} file(s) ready to upload")

        if st.session_state.get("ingested_preview"):
            with st.expander("📄 Ingested content preview", expanded=False):
                st.caption(st.session_state.ingested_preview)

        st.divider()

        # 6. INPUT SECTION expander (Compliance & Style Templates)
        with st.expander("INPUT SECTION", expanded=False):

            # Compliance Frameworks
            st.markdown("#### 📋 Compliance Frameworks")
            compliance_options = COMPLIANCE_FRAMEWORKS + ["Others"]
            selected_frameworks = st.multiselect(
                "Select applicable compliance frameworks:",
                compliance_options,
                key="compliance_select",
                default=st.session_state.get("selected_compliance_frameworks", [])
            )
            st.session_state.selected_compliance_frameworks = selected_frameworks

            if "Others" in selected_frameworks:
                custom_framework = st.text_input(
                    "Custom Compliance Framework",
                    value=st.session_state.get("custom_compliance_framework", ""),
                    placeholder="Enter custom compliance framework",
                    key="custom_compliance_input",
                    label_visibility="collapsed",
                )
                st.session_state.custom_compliance_framework = custom_framework

            total = len(selected_frameworks)
            if total:
                st.success(f"✓ {total} framework(s) selected")

            # Style Templates (upload only — no sample dropdown)
            st.markdown("#### 🎨 Style Templates")
            template_file = st.file_uploader(
                "Upload style template",
                type=["pptx", "docx"],
                key="template_uploader"
            )
            if template_file:
                st.session_state.uploaded_template = template_file
                st.success(f"✓ '{template_file.name}' uploaded")
