from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.helpers import reply
from core.report_manager import ReportManager
from utils.time_utils import is_valid_24h_time
from config.constants import (
    GROUP_CHAT_ID,
    SFT_TOPIC_ID,
    MOVEMENT_TOPIC_ID,
    ADMIN_IDS
)
from services.db_service import DatabaseService


# =========================
# CALLBACK ROUTER
# =========================
def callback_router(update, context):
    mode = context.user_data.get("mode")

    if mode == "MOVEMENT":
        handle_movement_callbacks(update, context)
    elif mode == "SFT":
        handle_sft_callbacks(update, context)


# =========================
# MOVEMENT CALLBACKS
# =========================
def handle_movement_callbacks(update, context):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == "mov:confirm":
        msg = context.user_data["final_message"]

        context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=MOVEMENT_TOPIC_ID,
            text=msg
        )

        for admin in ADMIN_IDS:
            context.bot.send_message(
                chat_id=admin,
                text="Movement report sent:\n\n" + msg
            )

        reply(update, "✅ Movement report sent.")


def movement_text_input(update, context):
    if context.user_data.get("mode") != "MOVEMENT":
        return

    if not context.user_data.get("awaiting_time"):
        return

    value = update.message.text.strip()

    if not is_valid_24h_time(value):
        reply(update, "❌ Invalid time format (HHMM).")
        return

    context.user_data["time"] = value
    context.user_data["awaiting_time"] = False

    msg = ReportManager.build_movement_message(
        names=context.user_data["selected"],
        from_loc=context.user_data["from"],
        to_loc=context.user_data["to"],
        time_hhmm=value
    )

    context.user_data["final_message"] = msg

    keyboard = [[
        InlineKeyboardButton("✅ Confirm & Send", callback_data="mov:confirm")
    ]]

    reply(
        update,
        "📋 Preview\n\n" + msg,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# SFT CALLBACKS
# =========================
def handle_sft_callbacks(update, context):
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith("sft:confirm"):
        if update.effective_user.id not in ADMIN_IDS:
            reply(update, "❌ Unauthorized")
            return

        today = context.user_data["date"]
        sir = context.user_data["sir"]

        records = DatabaseService.get_sft_by_date(today)

        msg = ReportManager.build_sft_message(
            sir_name=sir,
            date=today,
            records=records
        )

        context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=SFT_TOPIC_ID,
            text=msg
        )

        reply(update, "✅ SFT summary sent.")
