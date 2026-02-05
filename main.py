from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

from config.settings import BOT_TOKEN
from bot.commands import start, start_sft, start_movement
from bot.callbacks import callback_router, text_input_router
from services.db_service import DatabaseService


def setup_handlers(dispatcher):
    # -----------------------------
    # Command Handlers
    # -----------------------------
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("start_sft", start_sft))
    dispatcher.add_handler(CommandHandler("start_movement", start_movement))

    # -----------------------------
    # Callback Handlers (Inline Buttons)
    # -----------------------------
    dispatcher.add_handler(CallbackQueryHandler(callback_router))

    # -----------------------------
    # Text Input Handler
    # (Used for manual time entry, etc.)
    # -----------------------------
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, text_input_router)
    )


def main():
    # -----------------------------
    # Initialise Services
    # -----------------------------
    DatabaseService.initialise()

    # -----------------------------
    # Initialise Bot
    # -----------------------------
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    setup_handlers(dispatcher)

    # -----------------------------
    # Start Bot
    # -----------------------------
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
