import os
import tempfile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import date

from db.database import SessionLocal
from db.parade import generate_parade_state
from db.import_users_csv import import_users
from config.settings import BOT_TOKEN


def start(update, context: CallbackContext):
    update.message.reply_text("OCS Parade Test Bot is running.")

def parade(update, context: CallbackContext):
    db = SessionLocal()
    data = generate_parade_state(db, date.today())
    db.close()

    text = (
        f"TOTAL STRENGTH: {data['total_strength']}\n\n"
        f"CURRENT STRENGTH: {data['current_strength']}\n"
        f"OUT OF CAMP: {data['out_of_camp']}\n\n"
    )

    for status, count in data["status_counts"].items():
        text += f"{status}: {count}\n"
        for line in data["status_text"][status]:
            text += f"- {line}\n"
        text += "\n"

    update.message.reply_text(text)

def register(update, context: CallbackContext):
    if not update.message or not update.message.document:
        update.message.reply_text(
            "Send /register with a CSV file attached.\n"
            "Required columns: telegram_username, full_name, rank, role."
        )
        return

    document = update.message.document
    if document.file_size and document.file_size > 5 * 1024 * 1024:
        update.message.reply_text("CSV is too large (max 5MB).")
        return

    file_name = document.file_name or ""
    if not file_name.lower().endswith(".csv"):
        update.message.reply_text("Please upload a .csv file.")
        return

    temp_path = None
    try:
        telegram_file = document.get_file()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            temp_path = tmp.name
        telegram_file.download(custom_path=temp_path)

        import_users(temp_path, require_username=True)
        update.message.reply_text("CSV import complete.")
    except Exception as exc:
        update.message.reply_text(f"CSV import failed: {exc}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

def register_document(update, context: CallbackContext):
    # For /register sent as a caption on a document
    if not update.message or not update.message.caption:
        return
    if not update.message.caption.strip().startswith("/register"):
        return
    register(update, context)

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("parade", parade))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(MessageHandler(Filters.document & Filters.caption_regex(r"^/register"), register_document))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
