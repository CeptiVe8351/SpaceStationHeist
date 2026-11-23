import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from google import genai
import random

# ================================================================
# 1. PAGE SETUP
# ================================================================

st.set_page_config(
    page_title="Space Station Heist",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 SPACE STATION HEIST")
st.caption("NOVA AI SYSTEM // MISSION: STEAL THE STAR CORE")

# ================================================================
# 2. GEMINI SETUP
# ================================================================

load_dotenv(Path(__file__).resolve().with_name(".env"))
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None