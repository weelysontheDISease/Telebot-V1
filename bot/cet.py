from config.constants import (
    IC_GROUP_CHAT_ID,
    CET_TOPIC_ID,
    CADET_CET_TOPIC_ID,
    CADET_CHAT_ID,
    CET_KEYWORDS,
)
from telegram import Update
from telegram.ext import ContextTypes


async def cet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg or not msg.text:
        return

    if msg.chat_id != IC_GROUP_CHAT_ID:
        return

    if msg.message_thread_id != CET_TOPIC_ID:
        return

    if all(word.lower() in msg.text.lower() for word in CET_KEYWORDS):
        await context.application.bot.copy_message(
            chat_id=CADET_CHAT_ID,
            message_thread_id=CADET_CET_TOPIC_ID,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id,
        )

        cet_title = msg.text.split("\n")[0]
        print(f"--- {cet_title} sent ---")
