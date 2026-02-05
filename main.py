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
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("start_sft", start_sft))
    dispatcher.add_handler(CommandHandler("start_movement", start_movement))

    dispatcher.add_handler(CallbackQueryHandler(callback_router))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, text_input_router)
    )


def main():
    DatabaseService.initialise()

    updater = Updater(token=BOT_TOKEN, use_context=True)
    setup_handlers(updater.dispatcher)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
