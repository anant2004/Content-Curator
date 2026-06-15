"""
Prompt Bar Component

Renders prompt input area with:
- File upload zone (triggers backend ingest on upload)
- Text prompt input
- Generation options (num_slides, audience, tone, focus)
- Generate button → ingest (if no file yet) → generate slides
- Progress indication
"""

import streamlit as st
from streamlit_app import state
from streamlit_app.api_client import get_api_client


def render_prompt_bar():
    """Render the prompt bar component."""
    st.markdown("### 📝 Generate Content")

    # ── Mock / Live indicator ──────────────────────────────────────
    if state.is_mock_mode():
        st.warning("🔴 Mock Mode — backend calls are skipped. Toggle in sidebar.")

    # ── File Upload Zone ───────────────────────────────────────────
    col1, col2 = st.columns([3, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "📎 Upload Documents (PDF, DOCX, PPTX, EML, TXT)",
            type=["pdf", "docx", "pptx", "eml", "txt"],
            accept_multiple_files=True,
            key="file_uploader",
        )

        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"✓ {len(uploaded_files)} file(s) ready to upload")

    with col2:
        if st.button("🗑️", use_container_width=True, help="Clear all uploads"):
            st.session_state.uploaded_files = []
            st.session_state.session_id = None
            st.session_state.ingested_preview = ""
            st.rerun()

    # Show ingestion preview if a file was already ingested this session
    if st.session_state.get("ingested_preview"):
        with st.expander("📄 Ingested content preview", expanded=False):
            st.caption(st.session_state.ingested_preview)

    # ── Prompt Input ───────────────────────────────────────────────
    st.markdown("#### Your Prompt")
    prompt = st.text_area(
        "Describe what you want to generate...",
        value=st.session_state.get("current_prompt", ""),
        height=100,
        key="prompt_input",
        placeholder=(
            "e.g., Create a safety training presentation for blast furnace operations..."
        ),
    )
    st.session_state.current_prompt = prompt

    # ── Generation Options ─────────────────────────────────────────
    with st.expander("⚙️ Generation Options", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            num_slides = st.slider("Number of slides", 3, 20, 8, key="num_slides")
            tone = st.selectbox(
                "Tone",
                ["professional", "casual", "academic", "executive"],
                key="tone_select",
            )
        with col_b:
            audience = st.text_input(
                "Target audience",
                value="general audience",
                key="audience_input",
            )
            focus = st.text_input(
                "Focus area (optional)",
                value="",
                placeholder="e.g., safety statistics, cost reduction",
                key="focus_input",
            )

    # ── Advanced Options ───────────────────────────────────────────
    from streamlit_app.components.advanced_options import render_advanced_options
    render_advanced_options()

    # ── Generate Button ────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        generate_disabled = (
            not prompt.strip() or state.is_generating()
        )
        if st.button(
            "✨ Generate Content",
            use_container_width=True,
            type="primary",
            disabled=generate_disabled,
        ):
            _handle_generate(
                prompt=prompt,
                num_slides=num_slides,
                audience=audience,
                tone=tone,
                focus=focus,
            )

    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.current_prompt = ""
            st.rerun()

    # ── Progress ───────────────────────────────────────────────────
    if state.is_generating():
        st.info("⏳ Talking to the backend — this may take 20-60 seconds for LLM calls...")
        st.progress(0.5)


# ── Handler ────────────────────────────────────────────────────────────


def _handle_generate(
    prompt: str,
    num_slides: int = 8,
    audience: str = "general audience",
    tone: str = "professional",
    focus: str = "",
):
    """
    Full ingest → generate pipeline.

    Flow:
      1. If files uploaded → POST /api/v1/ingest/upload for each file
         Else → POST /api/v1/ingest/paste with the user's prompt text
      2. Store returned session_id in st.session_state
      3. POST /api/v1/generate/slides with the session_id
      4. Store slides in st.session_state for preview & export
    """
    if not prompt.strip():
        st.error("Please enter a prompt")
        return

    state.set_generating(True)

    try:
        # Add user message to chat history
        from streamlit_app.components.chat import add_user_message, add_assistant_message
        add_user_message(prompt)

        # ── MOCK MODE ─────────────────────────────────────────────
        if state.is_mock_mode():
            _handle_generate_mock(prompt)
            return

        api = get_api_client()

        # ── STEP 1: INGEST ────────────────────────────────────────
        uploaded_files = st.session_state.get("uploaded_files") or []
        session_id = st.session_state.get("session_id")  # reuse if already ingested

        if not session_id:
            if uploaded_files:
                # Ingest the first file (backend stores per session; handle one at a time)
                with st.spinner("📤 Uploading and ingesting document…"):
                    ingest_resp = api.ingest_file(uploaded_files[0])

                if "error" in ingest_resp:
                    st.error(f"Ingestion failed: {ingest_resp['error']}")
                    add_assistant_message(f"❌ Ingestion failed: {ingest_resp['error']}")
                    return

                session_id = ingest_resp["session_id"]
                state.set_session_id(session_id)
                st.session_state.ingested_preview = ingest_resp.get("preview", "")
                st.success(
                    f"✓ Document ingested ({ingest_resp.get('char_count', 0):,} characters)"
                )

            else:
                # No file — ingest the prompt text itself as source material
                with st.spinner("📥 Ingesting your prompt as source text…"):
                    ingest_resp = api.ingest_text(prompt, label="user_prompt")

                if "error" in ingest_resp:
                    st.error(f"Ingestion failed: {ingest_resp['error']}")
                    add_assistant_message(f"❌ Ingestion failed: {ingest_resp['error']}")
                    return

                session_id = ingest_resp["session_id"]
                state.set_session_id(session_id)

        # ── STEP 2: GENERATE ──────────────────────────────────────
        with st.spinner("🤖 Generating slides — this may take a moment…"):
            gen_resp = api.generate_slides(
                session_id=session_id,
                num_slides=num_slides,
                audience=audience,
                tone=tone,
                focus=focus or None,
            )

        if "error" in gen_resp:
            st.error(f"Generation failed: {gen_resp['error']}")
            add_assistant_message(f"❌ Generation failed: {gen_resp['error']}")
            return

        slides = gen_resp.get("slides", [])
        title = gen_resp.get("presentation_title", "Presentation")
        state.set_generated_slides(slides, title)

        # Store as active asset so preview panel picks it up
        state.set_active_asset(
            "presentation",
            {
                "id": session_id,
                "title": title,
                "slides": slides,
                "total_slides": gen_resp.get("total_slides", len(slides)),
            },
        )

        add_assistant_message(
            f"✅ Generated **{title}** — {len(slides)} slides ready. "
            "You can preview and export on the right."
        )
        st.success(f"✓ {len(slides)} slides generated!")

    except Exception as e:
        st.error(f"Unexpected error: {e}")

    finally:
        state.set_generating(False)
        st.rerun()


def _handle_generate_mock(prompt: str):
    """
    Mock generation path — uses the pre-built mock data instead of
    calling the backend. Useful for UI development / offline demo.
    """
    from streamlit_app.config import PRESENTATION_SLIDES
    from streamlit_app.components.chat import add_assistant_message

    mock_slides = PRESENTATION_SLIDES
    title = "Mock Presentation (offline)"
    state.set_generated_slides(mock_slides, title)
    state.set_active_asset(
        "presentation",
        {"id": "mock", "title": title, "slides": mock_slides},
    )
    add_assistant_message("✅ Loaded mock presentation (offline mode).")
    st.success("✓ Mock content loaded!")
