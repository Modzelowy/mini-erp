# app/style_loader.py (Clean version)
import streamlit as st


def load_css() -> None:
    """Loads the global CSS file."""
    css_file_path = "assets/style.css"
    try:
        with open(css_file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found. Check Dockerfile COPY instruction for 'assets'.")
