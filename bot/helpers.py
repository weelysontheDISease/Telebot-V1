def reply(update, text, reply_markup=None, parse_mode=None):
    if update.message:
        update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    else:
        update.callback_query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
