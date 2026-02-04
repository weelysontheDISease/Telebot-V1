<<<<<<< Updated upstream
=======
from bot.helpers import reply
from services.user_service import UserService


def start_sft(update, context):
    try:
        UserService.require_user(update.effective_user.id)
    except PermissionError as e:
        reply(update, f"❌ {e}")
        return

    context.user_data.clear()
    context.user_data["mode"] = "SFT"
    reply(update, "🏋️ SFT mode started.\nUse the buttons to proceed.")

def start_movement(update, context):
    try:
        UserService.require_user(update.effective_user.id)
    except PermissionError as e:
        reply(update, f"❌ {e}")
        return

    context.user_data.clear()
    context.user_data["mode"] = "MOVEMENT"
    context.user_data["selected"] = set()

    reply(update, "🚶 Movement mode started.\nSelect personnel.")
>>>>>>> Stashed changes
