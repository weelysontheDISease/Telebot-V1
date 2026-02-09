from config.settings import BOT_TOKEN
from services.db_service import DatabaseService
from bot.cet import cet_handler

from bot.commands import (
    start,
    start_sft,
    start_movement,
)

from bot.callbacks import (
    callback_router,
    text_input_router,
)

from utils.time_utils import SG_TZ, DAILY_MSG_TIME
from bot.daily_msg import send_daily_msg

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config.settings import BOT_TOKEN
from bot.commands import (
    start_sft,
    start_movement,
    start_status,
    start_parade_state
)
from bot.callbacks import (
    callback_router,
    text_input_router,
    register_status_handlers
)

from config.settings import BOT_TOKEN
from bot.commands import start, start_sft, start_movement
from bot.callbacks import callback_router, text_input_router
from services.db_service import DatabaseService


def main():
    print("BOOT: main entered", flush=True)

    # -----------------------------
    # Initialise Database
    # -----------------------------
    DatabaseService.initialise()

    # -----------------------------
    # Build Telegram Application
    # -----------------------------
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # -----------------------------
    # Command Handlers
    # -----------------------------

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cet_handler))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("start_sft", start_sft))
    application.add_handler(CommandHandler("start_status", start_status))
    application.add_handler(CommandHandler("start_movement", start_movement))
    register_status_handlers(application)


    # -----------------------------
    # Callback Handlers (Buttons)
    # -----------------------------
    application.add_handler(CallbackQueryHandler(callback_router))

    # -----------------------------
    # Text Input Handler
    # (movement manual time, etc.)
    # -----------------------------
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_input_router)
    )

    # -----------------------------
    # Job Queue (Daily Message)
    # -----------------------------
    application.job_queue.scheduler.timezone = SG_TZ
    application.job_queue.run_daily(
        send_daily_msg,
        time=DAILY_MSG_TIME,
    )

    # -----------------------------
    # Start Bot (Polling)
    # -----------------------------
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()
