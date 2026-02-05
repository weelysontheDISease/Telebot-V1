from bot.cet import cet_handler
from bot.parade_state import generate_parade_state
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters
)

from config.settings import BOT_TOKEN
from bot.commands import (
    start_sft,
    start_movement,
    start_cet,
    start_status,
    start_parade_state
)
from bot.callbacks import (
    callback_router,
    text_input_router
)
from services.db_service import DatabaseService

from utils.time_utils import SG_TZ, DAILY_MSG_TIME

from bot.daily_msg import send_daily_msg


def main():
    """
    Entry point for the Operations Telegram Bot.
    Responsible only for:
    - Initialising services
    - Registering handlers
    - Starting the bot
    """

    # -----------------------------
    # Initialise Database
    # -----------------------------
    DatabaseService.initialise()

    # -----------------------------
    # Initialise Telegram Bot
    # -----------------------------
    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    # -----------------------------
    # Command Handlers
    # -----------------------------
    dispatcher.add_handler(CommandHandler("start_sft", start_sft))
    dispatcher.add_handler(CommandHandler("start_movement", start_movement))
    dispatcher.add_handler(CommandHandler("start_cet", start_cet))
    dispatcher.add_handler(CommandHandler("start_status", start_status))
    dispatcher.add_handler(CommandHandler("start_paradestate", start_parade_state))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, cet_handler))


    # -----------------------------
    # Callback Handlers (Buttons)
    # -----------------------------
    dispatcher.add_handler(CallbackQueryHandler(callback_router))

    # -----------------------------
    # Text Input Handler
    # (Used for manual time, remarks, etc.)
    # -----------------------------
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, text_input_router)
    )

    # -----------------------------
    # Sechdule Jobs
    # -----------------------------
    updater.job_queue.scheduler.timezone = SG_TZ
    updater.job_queue.run_daily(
        send_daily_msg,
        time = DAILY_MSG_TIME
    )

    # -----------------------------
    # Start Bot
    # -----------------------------
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
