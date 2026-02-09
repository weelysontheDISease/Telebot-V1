from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers import reply
from core.report_manager import ReportManager
from utils.time_utils import is_valid_24h_time
from config.constants import (
    IC_GROUP_CHAT_ID,
    SFT_TOPIC_ID,
    MOVEMENT_TOPIC_ID,
    ADMIN_IDS,
)
from services.db_service import DatabaseService


# =========================
# CALLBACK ROUTER
# =========================
from bot.sft_manager import handle_sft_callbacks
async def callback_router(update, context):
    mode = context.user_data.get("mode")
    if mode == "MOVEMENT":
        await handle_movement_callbacks(update, context)
    elif mode == "SFT":
        await handle_sft_callbacks(update, context)


# =========================
# TEXT INPUT ROUTER
# =========================
async def text_input_router(update, context):
    mode = context.user_data.get("mode")

    if mode == "MOVEMENT":
        await movement_text_input(update, context)


# =========================
# MOVEMENT CALLBACKS
# =========================
async def handle_movement_callbacks(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "mov:confirm":
        msg = context.user_data["final_message"]

        # Send to IC group
        await context.bot.send_message(
            chat_id=IC_GROUP_CHAT_ID,
            message_thread_id=MOVEMENT_TOPIC_ID,
            text=msg,
        )

        # Notify admins
        for admin in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin,
                text="Movement report sent:\n\n" + msg,
            )

        await reply(update, "✅ Movement report sent.")


# =========================
# MOVEMENT TEXT INPUT
# =========================
async def movement_text_input(update, context):
    if context.user_data.get("mode") != "MOVEMENT":
        return

    if not context.user_data.get("awaiting_time"):
        return

    value = update.message.text.strip()

    if not is_valid_24h_time(value):
        await reply(update, "❌ Invalid time format (HHMM).")
        return

    context.user_data["time"] = value
    context.user_data["awaiting_time"] = False

    msg = ReportManager.build_movement_message(
        names=context.user_data["selected"],
        from_loc=context.user_data["from"],
        to_loc=context.user_data["to"],
        time_hhmm=value,
    )

    context.user_data["final_message"] = msg

    keyboard = [[
        InlineKeyboardButton("✅ Confirm & Send", callback_data="mov:confirm")
    ]]

    await reply(
        update,
        "📋 Preview\n\n" + msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# SFT CALLBACKS
# =========================
async def handle_sft_callbacks(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("sft:confirm"):
        if update.effective_user.id not in ADMIN_IDS:
            await reply(update, "❌ Unauthorized")
            return

        today = context.user_data["date"]
        sir = context.user_data["sir"]

        records = DatabaseService.get_sft_by_date(today)

        msg = ReportManager.build_sft_message(
            sir_name=sir,
            date=today,
            records=records,
        )

        await context.bot.send_message(
            chat_id=IC_GROUP_CHAT_ID,
            message_thread_id=SFT_TOPIC_ID,
            text=msg,
        )

        await reply(update, "✅ SFT summary sent.")
