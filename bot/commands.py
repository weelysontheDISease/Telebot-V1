from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers import reply
from config.constants import ACTIVITIES


# =========================
# START ENTRY POINT
# =========================
async def start(update, context):
    context.user_data.clear()
    await reply(
        update,
        "👋 Welcome.\n\n"
        "Use /start_sft for SFT reporting or /start_movement for movement reporting."
    )


# =========================
# SFT ENTRY POINT
# =========================
async def start_sft(update, context):
    context.user_data.clear()
    context.user_data["mode"] = "SFT"

    keyboard = []

    for item in ACTIVITIES:
        # Split "Gym @ Wingline" → ("Gym", "Wingline")
        activity, location = item.split(" @ ", 1)

        keyboard.append([
            InlineKeyboardButton(
                item,  # UI keeps the "@"
                callback_data=f"sft_activity|{activity}|{location}"
            )
        ])

    await reply(
        update,
        "🏋️ SFT mode started.\n\nSelect activity:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# MOVEMENT ENTRY POINT
# =========================
async def start_movement(update, context):
    context.user_data.clear()
    context.user_data["mode"] = "MOVEMENT"
    context.user_data["selected"] = set()

    await reply(
        update,
        "🚶 Movement reporting started.\n\n"
        "Select personnel using the buttons."
    )


# =========================
# STATUS REPORTING MENU
# =========================
def start_status(update, context):
    """Main menu for RSO/MA/RSI reporting"""
    context.user_data.clear()

    keyboard = [
        [InlineKeyboardButton("📋 Report RSO", callback_data="status_menu|report_rso")],
        [InlineKeyboardButton("✏️ Update RSO", callback_data="status_menu|update_rso")],
        [InlineKeyboardButton("🏥 Report MA", callback_data="status_menu|report_ma")],
        [InlineKeyboardButton("✏️ Update MA", callback_data="status_menu|update_ma")],
        [InlineKeyboardButton("🤒 Report RSI", callback_data="status_menu|report_rsi")],
        [InlineKeyboardButton("✏️ Update RSI", callback_data="status_menu|update_rsi")],
        [InlineKeyboardButton("❌ Cancel", callback_data="status_menu|cancel")]
    ]

    reply(
        update,
        "📊 *Status Reporting Menu*\n\n"
        "Select an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
