import pytz
from datetime import datetime, timedelta
import re

SG_TZ = pytz.timezone("Asia/Singapore")


def today_sg() -> str:
    return datetime.now(SG_TZ).strftime("%d%m%Y")


def now_hhmm() -> str:
    return datetime.now(SG_TZ).strftime("%H%M")


def is_valid_24h_time(value: str) -> bool:
    return bool(re.fullmatch(r"([01][0-9]|2[0-3])[0-5][0-9]", value))


def build_time_options(start_hour=7, end_hour=21, step_minutes=30):
    options = []
    current = datetime.now(SG_TZ).replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end = current.replace(hour=end_hour, minute=0)
    while current <= end:
        options.append(current.strftime("%H%M"))
        current += timedelta(minutes=step_minutes)
    return options
