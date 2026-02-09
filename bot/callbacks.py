from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

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
from core.sft_manager import handle_sft_callbacks
async def callback_router(update, context):
    mode = context.user_data.get("mode")
    if mode == "MOVEMENT":
        await handle_movement_callbacks(update, context)
    elif mode == "SFT":
        await handle_sft_callbacks(update, context)


# =========================
# TEXT INPUT ROUTER
# =========================

def text_input_router(update, context):
    mode = context.user_data.get("mode")

    if mode == "MOVEMENT":
        movement_text_input(update, context)
        return

    if mode in {"report", "update", "ma_report", "rsi_report", "rsi_update", "update_ma"}:
        from bot.rso_handler import manual_input_handler
        manual_input_handler(update, context)

# =========================
# STATUS MENU HANDLER
# =========================

def status_menu_handler(update, context):
    query = update.callback_query
    query.answer()
    _, action = query.data.split("|", 1)

    if action == "report_rso":
        from bot.rso_handler import start_status_report
        start_status_report(update, context)
    elif action == "update_rso":
        from bot.rso_handler import start_update_status
        start_update_status(update, context)
    elif action == "report_ma":
        from bot.rso_handler import start_ma_report
        start_ma_report(update, context)
    elif action == "update_ma":
        from bot.rso_handler import update_endorsed
        update_endorsed(update, context)
    elif action == "report_rsi":
        from bot.rso_handler import start_rsi_report
        start_rsi_report(update, context)
    elif action == "update_rsi":
        from bot.rso_handler import start_update_rsi
        start_update_rsi(update, context)
    elif action == "cancel":
        context.user_data.clear()
        reply(update, "❌ Cancelled. Use /start_status to begin again.")


def register_status_handlers(dispatcher):
    from bot.rso_handler import (
        name_selection_handler,
        confirm_handler,
        cancel,
        mc_days_button_handler,
        confirm_ma_handler,
        instructor_selection_handler,
        rsi_days_button_handler,
        rsi_status_type_handler,
        confirm_rsi_report_handler,
        confirm_rsi_update_handler,
    )

    dispatcher.add_handler(CallbackQueryHandler(status_menu_handler, pattern=r"^status_menu\|"))
    dispatcher.add_handler(CallbackQueryHandler(name_selection_handler, pattern=r"^(name|rsi_name|update_name|update_ma_name|rsi_update_name)\|"))
    dispatcher.add_handler(CallbackQueryHandler(mc_days_button_handler, pattern=r"^mc_days\|"))
    dispatcher.add_handler(CallbackQueryHandler(confirm_handler, pattern=r"^confirm$"))
    dispatcher.add_handler(CallbackQueryHandler(cancel, pattern=r"^cancel$"))
    dispatcher.add_handler(CallbackQueryHandler(confirm_ma_handler, pattern=r"^confirm_ma$"))
    dispatcher.add_handler(CallbackQueryHandler(instructor_selection_handler, pattern=r"^instructor\|"))
    dispatcher.add_handler(CallbackQueryHandler(rsi_days_button_handler, pattern=r"^rsi_days\|"))
    dispatcher.add_handler(CallbackQueryHandler(rsi_status_type_handler, pattern=r"^rsi_type\|"))
    dispatcher.add_handler(CallbackQueryHandler(confirm_rsi_report_handler, pattern=r"^confirm_rsi_report$"))
    dispatcher.add_handler(CallbackQueryHandler(confirm_rsi_update_handler, pattern=r"^confirm_rsi_update$"))

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
