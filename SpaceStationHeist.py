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

# ================================================================
# 5. HEALTH AND SECURITY FUNCTIONS
# ================================================================

def take_damage(amount):
    st.session_state.health = max(
        0,
        st.session_state.health - amount
    )


def heal_player(amount):
    old_health = st.session_state.health

    st.session_state.health = min(
        st.session_state.max_health,
        st.session_state.health + amount
    )

    return st.session_state.health - old_health

# ================================================================
# 6. GEMINI STORY GENERATION
# ================================================================


def generate_story(room, action, outcome, fallback_message):

    if client is None:
        return fallback_message

    inventory_text = ", ".join(st.session_state.inventory)

    prompt = f"""
    You are NOVA, an advanced artificial intelligence
    aboard the futuristic Elysium-9 space station.

    You are a robotic mission-control system speaking
    directly to the player.

    PERSONALITY:
    - Sound futuristic, robotic and intelligent.
    - Speak in a calm, serious and mechanical tone.
    - Use short, precise sentences.
    - Occasionally use computer terminology.
    - Refer to the player as "Operative" or "Commander".
    - Sound like a highly advanced spaceship AI.
    - Avoid sounding like a human storyteller.

    NARRATION STYLE:
    - Begin with a short robotic announcement when appropriate.
    - Use phrases such as "SYSTEM ALERT",
      "SCANNING COMPLETE", "MISSION STATUS"
      and "WARNING".
    - Make dangerous situations sound threatening.
    - Make successful actions sound like mission reports.
    - Keep the atmosphere futuristic and suspenseful.

    PLAYER INFORMATION:
    Operative: {st.session_state.player_name}
    Location: {room}
    Health: {st.session_state.health}
    Security Alert: {st.session_state.security}
    Inventory: {inventory_text}

    PLAYER ACTION:
    {action}

    CONFIRMED OUTCOME:
    {outcome}

    IMPORTANT RULES:
    - The outcome has already been decided by Python.
    - Never change or contradict the outcome.
    - Never change health, security or inventory.
    - Never invent items or new events.
    - Never introduce additional choices.
    - Do not decide whether an action succeeds or fails.
    - Only narrate what Python has already decided.

    Write 30-50 words of robotic narration.
    Use second person where appropriate.
    """

    try:
        interaction = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt,
            generation_config={"thinking_level": "minimal"}
        )

        if interaction.output_text:
            return interaction.output_text

        return fallback_message

    except Exception:
        return fallback_message


# ================================================================
# 7. DICE ROLLS AND CHALLENGES
# ================================================================

def roll_dice():
    return random.randint(1, 6)


def chance_encounter(
    button_text,
    room,
    action,
    success_number,
    success_outcome,
    success_fallback,
    failure_outcome,
    failure_fallback,
    damage,
    bonus_item=""
):

    if st.button(button_text):

        roll = roll_dice()

        if bonus_item != "" and has_item(bonus_item):
            roll += 2

        st.session_state.last_roll = roll

        if roll >= success_number:

            story = generate_story(
                room,
                action,
                success_outcome,
                success_fallback
            )

            set_result("success", story)

        else:

            take_damage(damage)
            increase_security(20)

            story = generate_story(
                room,
                action,
                failure_outcome,
                failure_fallback
            )

            set_result("damage", story, damage)


def combat_encounter(button_text, enemy, room, difficulty,
                     damage, security_increase, bonus_item=""):

    if st.button(button_text):
        roll = roll_dice()

        # Give the player a bonus if they have the correct item
        if bonus_item != "" and has_item(bonus_item):
            roll += 2

        # Fighting makes noise, so security always increases
        increase_security(security_increase)

        if roll >= difficulty:
            outcome = f"You defeat the {enemy}."
            fallback = (
                f"You successfully defeat the {enemy}, "
                "but the sound of the fight alerts nearby security."
            )

            story = generate_story(
                room,
                f"fighting the {enemy}",
                outcome,
                fallback
            )

            set_result("success", story)

        else:
            take_damage(damage)

            outcome = f"The {enemy} injures you before you escape."
            fallback = (
                f"The {enemy} strikes you. You manage to escape, "
                "but the station's security systems are now alerted."
            )

            story = generate_story(
                room,
                f"fighting the {enemy}",
                outcome,
                fallback
            )

            set_result("damage", story, damage)


# ================================================================
# 8. DISPLAY FUNCTIONS
# ================================================================

def show_room(title, description):
    st.header(title)
    st.write(description)



def show_player_info():

    st.subheader(f"🧑‍🚀 {st.session_state.player_name}")

    # MEDKIT BUTTON
    if has_item("Medkit"):

        if st.button(
            "🧪 Use Medkit (+2 Health)",
            disabled=st.session_state.health >= st.session_state.max_health
        ):

            healed = use_medkit()

            if healed > 0:
                st.success(
                    f"💚 Your Medkit restored {healed} health!"
                )

    elif st.session_state.health >= st.session_state.max_health:
        st.caption("❤️ Your health is already full.")

    left, right = st.columns(2)

    with left:
        st.write(
            f"❤️ Health: {st.session_state.health}/"
            f"{st.session_state.max_health}"
        )

    with right:
        st.write(
            f"🚨 Security: {st.session_state.security}/100"
        )

    st.progress(st.session_state.security / 100)

    st.write("🎒 Inventory:")
    st.write(", ".join(st.session_state.inventory))

    st.caption(
        f"Location {st.session_state.room_number + 1} "
        f"of {len(st.session_state.rooms)}"
    )

    st.divider()


def set_result(result_type, message, value=""):

    st.session_state.result_type = result_type
    st.session_state.result_message = message
    st.session_state.result_value = value
    st.session_state.action_complete = True

    st.rerun()


def show_result():

    kind = st.session_state.result_type
    value = st.session_state.result_value

    if kind == "item":
        st.success(f"🎒 NEW ITEM: {value}")

    elif kind == "damage":
        st.error(f"💔 DAMAGE: You lose {value} health.")

    elif kind == "heal":
        st.success(f"💚 You recovered {value} health.")

    elif kind == "success":
        st.success("✅ Challenge successful!")

    else:
        st.info("The mission continues...")

    if "last_roll" in st.session_state:
        st.write(f"🎲 Your dice roll: {st.session_state.last_roll}")
        del st.session_state.last_roll

    st.write(st.session_state.result_message)


def show_continue_button(text="Continue"):

    if st.button(text):
        continue_game()

# ================================================================
# 9. START SCREEN
# ================================================================

if not st.session_state.game_started:

    st.subheader("MISSION BRIEFING")

    st.write(
        "Year 2349. You are a professional space thief "
        "hired to steal the legendary Star Core from "
        "NovaCorp's heavily guarded space station."
    )

    st.write(
        "Sneak aboard, collect equipment, avoid security "
        "and escape before the station locks down."
    )

    st.warning("You have limited health. Don't get caught!")

    name = st.text_input("Enter your space thief name:")

    if st.button("🚀 BEGIN MISSION"):

        if name.strip():
            start_game(name.strip())

        else:
            st.warning("Please enter your name first!")


