<<<<<<< Updated upstream
=======
from bot.helpers import reply
from core.sft_manager import handle_sft_callback
from core.movement_manager import (
    handle_movement_callback,
    handle_manual_time,
)


# ==================================================
# CALLBACK ROUTER (INLINE BUTTONS)
# ==================================================
def callback_router(update, context):
    """
    Routes all inline keyboard callbacks based on the current mode.
    """

    if not update.callback_query:
        return

    mode = context.user_data.get("mode")

    if mode == "SFT":
        handle_sft_callback(update, context)
        return

    if mode == "MOVEMENT":
        handle_movement_callback(update, context)
        return

    # No active workflow
    update.callback_query.answer()
    reply(
        update,
        "❌ No active session.\n"
        "Please start with /start_sft or /start_movement."
    )


# ==================================================
# TEXT INPUT ROUTER (FREE TEXT)
# ==================================================
def text_input_router(update, context):
    """
    Routes free-text input (used mainly for manual movement time).
    """

    mode = context.user_data.get("mode")

    if mode == "MOVEMENT":
        handle_manual_time(update, context)
        return

    # Ignore text for other modes
>>>>>>> Stashed changes
