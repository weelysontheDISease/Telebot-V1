from bot.helpers import reply

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
    await reply(
        update,
        "🏋️ SFT mode started.\n\n"
        "Use the menu to submit or manage SFT."
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
