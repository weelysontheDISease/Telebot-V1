def reply(update, text, reply_markup=None, parse_mode=None):
    message = update.effective_message
    if not message:
        return None
    return message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
    )
