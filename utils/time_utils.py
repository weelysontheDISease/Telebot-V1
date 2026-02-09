import pytz
from datetime import datetime, time
import re
from db.crud import delete_expired_statuses_and_events

SG_TZ = pytz.timezone("Asia/Singapore")
DAILY_MSG_TIME = time(hour=8, minute=0)


def today_sg() -> str:
    return datetime.now(SG_TZ).strftime("%d%m%Y")


def day_sg() -> str:
    return datetime.now(SG_TZ).strftime("%A")


def now_hhmm() -> str:
    return datetime.now(SG_TZ).strftime("%H%M")


def is_valid_24h_time(value: str) -> bool:
    return bool(re.fullmatch(r"([01][0-9]|2[0-3])[0-5][0-9]", value))

def daily_reset(context=None):
    """Daily cleanup job to remove expired medical statuses/events."""
    today = datetime.now(SG_TZ).date()
    delete_expired_statuses_and_events(today)
