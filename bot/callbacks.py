from bot.helpers import reply
from core.sft_manager import handle_sft_callback
from core.movement_manager import handle_movement_callback, handle_manual_time


def callback_router(update, context):
    if not update.callback_query:
        return

    mode = context.user_data.get("mode")

    if mode == "SFT":
        handle_sft_callback(update, context)
        return

    if mode == "MOVEMENT":
        handle_movement_callback(update, context)
        return

    update.callback_query.answer()
    reply(
        update,
        "❌ No active session.\n"
        "Please start with /start_sft or /start_movement.",
    )


def text_input_router(update, context):
    mode = context.user_data.get("mode")

    if mode == "MOVEMENT":
        handle_manual_time(update, context)
