# app/main.py (FINAL CORRECTED VERSION)

import streamlit as st
from database import engine
from models import Base
from style_loader import load_css  # <-- THE MISSING IMPORT!

# --- Initial Database Setup ---
# This is the crucial line that was missing.
# It connects to the DB and creates all tables defined in models.py if they don't exist.
Base.metadata.create_all(bind=engine)
# --- End of Setup ---


# Set the page configuration. This should be the first Streamlit command.
st.set_page_config(page_title="Mini ERP Home", page_icon="👑", layout="wide")

load_css()


st.title("Welcome to your Mini ERP System! 👑")

st.header("This is your central command.")
st.write(
    "Use the navigation panel on the left to manage different parts of your system."
)
