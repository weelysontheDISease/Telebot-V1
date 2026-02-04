import pytz
from datetime import time
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from config.settings import BOT_TOKEN, TIMEZONE
from bot.menus import main_menu
from bot.commands import (
    join_sft,
    quit_sft,
    generate_sft,
    force_remove,
    debug_ids
)
from bot.callbacks import (
    menu_handler,
    button_handler,
    confirm_send,
    cancel_send,
    force_remove_confirm
)
from services.db_service import DatabaseService
from utils.time_utils import daily_reset
from bot.parade_state import generate_parade_state

def setup_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("start", main_menu))
    dispatcher.add_handler(CommandHandler("join_sft", join_sft))
    dispatcher.add_handler(CommandHandler("quit_sft", quit_sft))
    dispatcher.add_handler(CommandHandler("generate", generate_sft))
    dispatcher.add_handler(CommandHandler("force_remove", force_remove))
    dispatcher.add_handler(CommandHandler("debug_ids", debug_ids))
    dispatcher.add_handler(CommandHandler("parade_state", generate_parade_state))

    dispatcher.add_handler(
        CallbackQueryHandler(menu_handler, pattern="^menu_")
    )
    dispatcher.add_handler(
        CallbackQueryHandler(confirm_send, pattern="^confirm_send$")
    )
    dispatcher.add_handler(
        CallbackQueryHandler(cancel_send, pattern="^cancel_send$")
    )
    dispatcher.add_handler(
        CallbackQueryHandler(force_remove_confirm, pattern="^force_rm")
    )
    dispatcher.add_handler(
        CallbackQueryHandler(button_handler)
    )


def setup_jobs(job_queue):
    job_queue.scheduler.configure(timezone=pytz.timezone(TIMEZONE))
    job_queue.run_daily(
        daily_reset,
        time=time(hour=23, minute=59),
        name="daily_data_reset"
    )


def main():
    DatabaseService.initialise()

    updater = Updater(token=BOT_TOKEN)
    setup_handlers(updater.dispatcher)
    setup_jobs(updater.job_queue)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

