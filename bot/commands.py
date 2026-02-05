from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers import reply
from config.constants import PERSONNEL_NAMES, SFT_ACTIVITIES
from services.user_service import UserService
from utils.time_utils import build_time_options


def start(update, context):
    reply(
        update,
        "Welcome! Use /start_sft to submit SFT or /start_movement to report movement.",
    )


def start_sft(update, context):
    try:
        UserService.require_user(update.effective_user)
    except PermissionError as exc:
        reply(update, f"❌ {exc}")
        return

    context.user_data.clear()
    context.user_data["mode"] = "SFT"
    context.user_data["time_options"] = build_time_options()

    if not SFT_ACTIVITIES:
        reply(update, "❌ No SFT activities configured.")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{activity} @ {location}",
                callback_data=f"sft_activity|{activity}|{location}",
            )
        ]
        for activity, location in SFT_ACTIVITIES
    ]

    reply(update, "Select SFT activity:", InlineKeyboardMarkup(keyboard))


def start_movement(update, context):
    try:
        UserService.require_user(update.effective_user)
    except PermissionError as exc:
        reply(update, f"❌ {exc}")
        return

    context.user_data.clear()
    context.user_data["mode"] = "MOVEMENT"
    context.user_data["selected"] = set()
    context.user_data["all_names"] = PERSONNEL_NAMES

    keyboard = [
        [InlineKeyboardButton(f"⬜ {name}", callback_data=f"move_name|{name}")]
        for name in PERSONNEL_NAMES
    ]
    keyboard.append(
        [InlineKeyboardButton("✅ Done Selecting", callback_data="move_done")]
    )

    reply(update, "Select personnel moving:", InlineKeyboardMarkup(keyboard))
