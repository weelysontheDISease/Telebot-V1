from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.helpers import reply
from config.constants import ACTIVITIES, NAMES
from services.db_service import get_sft_window


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
    window = get_sft_window()

    if not window:
        await reply(
            update,
            "❌ PT SFT has not been opened by IC yet.\n"
            "Please wait for instructions."
        )
        return

    context.user_data.clear()
    context.user_data["mode"] = "SFT"
    context.user_data["start"] = window.start
    context.user_data["end"] = window.end
    context.user_data["date"] = window.date

    keyboard = [
        [
            InlineKeyboardButton(
                activity,
                callback_data=f"sft_activity|{activity}"
            )
        ]
        for activity in ACTIVITIES
    ]

    await reply(
        update,
        f"🏋️ *PT SFT Open*\n\n"
        f"Time: {window.start}-{window.end}\n\n"
        f"Select activity:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# MOVEMENT ENTRY POINT
# =========================
async def start_movement(update, context):
    context.user_data.clear()
    context.user_data["mode"] = "MOVEMENT"
    context.user_data["selected"] = set()
    context.user_data["all_names"] = NAMES

    keyboard = [
        [
            InlineKeyboardButton(
                f"⬜ {name}",
                callback_data=f"mov:name|{name}"
            )
        ]
        for name in NAMES
    ]

    keyboard.append(
        [InlineKeyboardButton("✅ Done Selecting", callback_data="mov:done")]
    )

    await reply(
        update,
        "🚶 *Movement reporting started*\n\nSelect personnel:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# STATUS REPORTING MENU
# =========================
async def start_status(update, context):
    """Main menu for RSO/MA/RSI reporting"""
    context.user_data.clear()

    keyboard = [
        [InlineKeyboardButton("📋 Report RSO", callback_data="status_menu|report_rso")],
        [InlineKeyboardButton("✏️ Update RSO", callback_data="status_menu|update_rso")],
        [InlineKeyboardButton("🏥 Report MA", callback_data="status_menu|report_ma")],
        [InlineKeyboardButton("✏️ Update MA", callback_data="status_menu|update_ma")],
        [InlineKeyboardButton("🤒 Report RSI", callback_data="status_menu|report_rsi")],
        [InlineKeyboardButton("✏️ Update RSI", callback_data="status_menu|update_rsi")],
        [InlineKeyboardButton("❌ Cancel", callback_data="status_menu|cancel")],
    ]

    await reply(
        update,
        "📊 *Status Reporting Menu*\n\nSelect an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )
