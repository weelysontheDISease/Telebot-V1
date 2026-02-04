from bot.helpers import reply


# =========================
# SFT ENTRY POINT
# =========================
def start_sft(update, context):
    context.user_data.clear()
    context.user_data["mode"] = "SFT"
    reply(
        update,
        "🏋️ SFT mode started.\n\n"
        "Use the menu to submit or manage SFT."
    )


# =========================
# MOVEMENT ENTRY POINT
# =========================
def start_movement(update, context):
    context.user_data.clear()
    context.user_data["mode"] = "MOVEMENT"
    context.user_data["selected"] = set()
    reply(
        update,
        "🚶 Movement reporting started.\n\n"
        "Select personnel using the buttons."
    )
