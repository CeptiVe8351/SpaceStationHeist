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

# ================================================================
# 3. GAME SETUP
# ================================================================

if "game_started" not in st.session_state:
    st.session_state.game_started = False


def start_game(name):
    """Start a new game and initialise all values."""

    st.session_state.game_started = True
    st.session_state.player_name = name

    st.session_state.health = 5
    st.session_state.max_health = 5

    st.session_state.security = 0
    st.session_state.inventory = ["Hacking Device"]

    st.session_state.rooms = [
        "docking_bay",
        "engineering",
        "storage",
        "security",
        "control_room",
        "vault",
        "escape_bay"
    ]

    st.session_state.room_number = 0

    st.session_state.action_complete = False
    st.session_state.result_type = ""
    st.session_state.result_message = ""
    st.session_state.result_value = ""

    st.rerun()


def increase_security(amount):
    st.session_state.security += amount
    if st.session_state.security > 100:
        st.session_state.security = 100


def restart_game():
    st.session_state.clear()
    st.rerun()


def get_current_room():
    return st.session_state.rooms[st.session_state.room_number]


def continue_game():
    """Move to the next location."""

    st.session_state.result_type = ""
    st.session_state.result_message = ""
    st.session_state.result_value = ""
    st.session_state.action_complete = False

    st.session_state.room_number += 1
    st.rerun()


def retry_action():
    st.session_state.action_complete = False
    st.session_state.result_type = ""
    st.session_state.result_message = ""
    st.session_state.result_value = ""
    st.rerun()


# ================================================================
# 4. INVENTORY FUNCTIONS
# ================================================================

def add_item(item):
    if item not in st.session_state.inventory:
        st.session_state.inventory.append(item)


def has_item(item):
    return item in st.session_state.inventory


def remove_item(item):
    if item in st.session_state.inventory:
        st.session_state.inventory.remove(item)



def use_medkit():
    if has_item("Medkit"):

        healed = heal_player(2)

        # Only use the Medkit if health was actually restored
        if healed > 0:
            remove_item("Medkit")

        return healed

    return 0
