from config.constants import IC_GROUP_CHAT_ID, CET_TOPIC_ID, CADET_CET_TOPIC_ID, CADET_CHAT_ID, CET_KEYWORDS


def cet_handler(update, context):
    msg = update.message

    if not msg or not msg.text:
        return

    if msg.chat_id != IC_GROUP_CHAT_ID:
        return

    if msg.message_thread_id != CET_TOPIC_ID:
        return
    
    first_line = msg.text.split("\n")[0]


    if CET_KEYWORDS.lower() in first_line.lower():
        context.bot.copy_message(
            chat_id = CADET_CHAT_ID,
            message_thread_id = CADET_CET_TOPIC_ID,
            from_chat_id = msg.chat_id,
            message_id = msg.message_id
        )
    
    print(f"--- {first_line} sent ---")