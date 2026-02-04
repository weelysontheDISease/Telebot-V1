<<<<<<< Updated upstream
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
=======
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

from config.settings import BOT_TOKEN
from config.constants import IC_GROUP_CHAT_ID

from bot.cet import cet_handler
from bot.commands import (
    start_sft,
    start_movement,
    start_status,
    start_parade_state,
)
from bot.callbacks import (
    callback_router,
    text_input_router,
>>>>>>> Stashed changes
)
from services.db_service import DatabaseService
from utils.time_utils import daily_reset


def setup_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("start", main_menu))
    dispatcher.add_handler(CommandHandler("join_sft", join_sft))
    dispatcher.add_handler(CommandHandler("quit_sft", quit_sft))
    dispatcher.add_handler(CommandHandler("generate", generate_sft))
    dispatcher.add_handler(CommandHandler("force_remove", force_remove))
    dispatcher.add_handler(CommandHandler("debug_ids", debug_ids))

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

<<<<<<< Updated upstream
=======
    # -----------------------------
    # Command Handlers
    # -----------------------------
    dispatcher.add_handler(CommandHandler("start_sft", start_sft))
    dispatcher.add_handler(CommandHandler("start_movement", start_movement))
    dispatcher.add_handler(CommandHandler("start_status", start_status))
    dispatcher.add_handler(CommandHandler("start_paradestate", start_parade_state))

    # -----------------------------
    # CET AUTO-FORWARD (Instructor Chat)
    # Must be BEFORE generic text handler
    # -----------------------------
    dispatcher.add_handler(
        MessageHandler(
            Filters.chat(IC_GROUP_CHAT_ID) & Filters.text,
            cet_handler
        )
    )

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
    # Start Bot
    # -----------------------------
>>>>>>> Stashed changes
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

