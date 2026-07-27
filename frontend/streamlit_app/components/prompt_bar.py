"""
Prompt Bar Component

Renders prompt input area with:
- Text prompt input
- Generation options (num_slides single textbar, target audience, tone with Others option, focus area)
- Generate button → ingest (if file uploaded in sidebar) → generate content
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
        st.warning("🔴 Mock Mode — backend calls are skipped.")

    # ── Prompt Input ───────────────────────────────────────────────
    st.markdown("#### Your Prompt")
    prompt = st.text_area(
        "Describe what you want to generate...",
        value=st.session_state.get("current_prompt", ""),
        height=180,
        key="prompt_input",
        placeholder=(
            "e.g., Create a safety training presentation for blast furnace operations..."
        ),
    )
    st.session_state.current_prompt = prompt

    # ── Generation Options ─────────────────────────────────────────
    with st.expander("⚙️ Generation Options", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            num_slides = st.number_input(
                "Number of slides",
                min_value=1,
                max_value=100,
                value=int(st.session_state.get("num_slides_input", 8)),
                step=1,
                key="num_slides_input",
            )

            tone_option = st.selectbox(
                "Tone",
                ["professional", "casual", "academic", "executive", "Others"],
                key="tone_select",
            )
            if tone_option == "Others":
                custom_tone = st.text_input(
                    "Custom Tone",
                    value=st.session_state.get("custom_tone", ""),
                    placeholder="Enter custom tone",
                    key="custom_tone_input",
                    label_visibility="collapsed",
                )
                st.session_state.custom_tone = custom_tone
                tone = custom_tone if custom_tone.strip() else "professional"
            else:
                tone = tone_option

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
                num_slides=int(num_slides),
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
        st.info("⏳ Processing your request...")
        st.progress(0.5)


# ── Handler ────────────────────────────────────────────────────────────


def _handle_generate(
    prompt: str,
    num_slides: int = 8,
    audience: str = "general audience",
    tone: str = "professional",
    focus: str = "",
):
    """Full ingest → generate pipeline, wired to all sidebar metadata."""
    if not prompt.strip():
        st.error("Please enter a prompt")
        return

    state.set_generating(True)

    try:
        from streamlit_app.components.chat import add_user_message, add_assistant_message
        add_user_message(prompt)

        # ── MOCK MODE ─────────────────────────────────────────────
        if state.is_mock_mode():
            _handle_generate_mock(prompt)
            return

        api = get_api_client()

        # ── Read sidebar metadata ─────────────────────────────────
        domain = state.get_effective_domain()
        division = state.get_effective_division()
        output_type = state.get_effective_output_type()
        compliance_frameworks = state.get_effective_compliance_frameworks()

        uploaded_files = st.session_state.get("uploaded_files") or []
        existing_session_id = state.get_session_id()

        # ── STEP 1: INGEST ────────────────────────────────────────
        # Skip ingestion if the sidebar button already ingested this batch
        if existing_session_id:
            session_id = existing_session_id
            st.info(f"♻️ Re-using existing ingest session ({len(uploaded_files)} file(s) already processed).")
        elif uploaded_files:
            file_names = ", ".join(f.name for f in uploaded_files)
            with st.spinner(f"📤 Ingesting {len(uploaded_files)} file(s): {file_names}…"):
                ingest_resp = api.ingest_files(uploaded_files)

            if "error" in ingest_resp:
                st.error(f"Ingestion failed: {ingest_resp['error']}")
                add_assistant_message(f"❌ Ingestion failed: {ingest_resp['error']}")
                return

            session_id = ingest_resp["session_id"]
            state.set_session_id(session_id)
            st.session_state.ingested_preview = ingest_resp.get("preview", "")

            ok_names = ingest_resp.get("filenames", [ingest_resp.get("filename", file_names)])
            total_chars = ingest_resp.get("total_char_count", ingest_resp.get("char_count", 0))
            st.info(
                f"📄 Ingested **{len(ok_names)}** file(s) ({total_chars:,} characters)"
            )
            fail_names = ingest_resp.get("failed_filenames", [])
            if fail_names:
                st.warning(f"⚠️ Could not ingest: {', '.join(fail_names)}")
        else:
            # No files — ingest the prompt itself as the source text
            with st.spinner("📥 Ingesting your prompt as source text…"):
                ingest_resp = api.ingest_text(prompt, label="user_prompt")

            if "error" in ingest_resp:
                st.error(f"Ingestion failed: {ingest_resp['error']}")
                add_assistant_message(f"❌ Ingestion failed: {ingest_resp['error']}")
                return

            session_id = ingest_resp["session_id"]
            state.set_session_id(session_id)

        # ── STEP 2: GENERATE ──────────────────────────────────────
        context_parts = [p for p in [domain, division, output_type] if p]
        context_label = f" [{' · '.join(context_parts)}]" if context_parts else ""
        with st.spinner(f"🤖 Generating slides{context_label} — this may take a moment…"):
            gen_resp = api.generate_slides(
                session_id=session_id,
                num_slides=num_slides,
                audience=audience,
                tone=tone,
                focus=focus or None,
                user_prompt=prompt,
                domain=domain,
                division=division,
                output_type=output_type,
                compliance_frameworks=compliance_frameworks if compliance_frameworks else None,
            )

        if "error" in gen_resp:
            st.error(f"Generation failed: {gen_resp['error']}")
            add_assistant_message(f"❌ Generation failed: {gen_resp['error']}")
            return

        slides = gen_resp.get("slides", [])
        title = gen_resp.get("presentation_title", "Presentation")
        state.set_generated_slides(slides, title)

        state.set_active_asset(
            "presentation",
            {
                "id": session_id,
                "title": title,
                "slides": slides,
                "total_slides": gen_resp.get("total_slides", len(slides)),
            },
        )

        success_parts = [f"✅ Generated **{title}** — {len(slides)} slides ready."]
        if context_parts:
            success_parts.append(f"Context: {', '.join(context_parts)}")
        if compliance_frameworks:
            success_parts.append(f"Compliance: {', '.join(compliance_frameworks)}")
        add_assistant_message("\n".join(success_parts))
        st.success(f"✓ {len(slides)} slides generated!")

    except Exception as e:
        st.error(f"Unexpected error: {e}")

    finally:
        state.set_generating(False)
        st.rerun()


def _handle_generate_mock(prompt: str):
    """
    Mock generation path.
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
