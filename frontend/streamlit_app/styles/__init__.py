"""
Styles Module

Contains CSS styling and theme utilities for Streamlit app.
"""

import streamlit as st
from pathlib import Path


def style_app():
    """Load and apply custom CSS styling to the app."""
    # Critical inline overrides — applied before external CSS so nothing renders dark
    st.markdown(
        """
        <style>
        .stApp, [data-testid="stAppViewContainer"] { color-scheme: light !important; }
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            color: #1F2937 !important;
        }
        section[data-testid="stSidebar"] div[data-baseweb="select"],
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #1F2937 !important;
            border: 1px solid #DCE3EC !important;
        }
        section[data-testid="stSidebar"] div[data-baseweb="select"] input {
            color: #1F2937 !important;
            -webkit-text-fill-color: #1F2937 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    css_path = Path(__file__).parent / "style.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


__all__ = ["style_app"]
