from config.constants import DAILY_MSGS, CADET_CHAT_ID
from utils.time_utils import day_sg


def send_daily_msg(context):

    today = day_sg()
    if today in DAILY_MSGS:
            context.bot.send_message(
            chat_id = CADET_CHAT_ID, 
            text = DAILY_MSGS[today],
            parse_mode = "HTML"
        )
    
    print(f"---- {today} message sent ----")
