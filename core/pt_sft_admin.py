import re
from datetime import datetime
import pytz

from bot.helpers import reply
from services.db_service import set_sft_window
from config.constants import ADMIN_IDS

SG_TZ = pytz.timezone("Asia/Singapore")


def today_sg():
    return datetime.now(SG_TZ).strftime("%d%m%Y")


def _valid_time_range(text: str):
    """
    Expects HHMM-HHMM
    """
    if not re.fullmatch(r"\d{4}-\d{4}", text):
        return None

    start, end = text.split("-")

    if not (start < end):
        return None

    hh1, mm1 = int(start[:2]), int(start[2:])
    hh2, mm2 = int(end[:2]), int(end[2:])

    if hh1 > 23 or hh2 > 23 or mm1 > 59 or mm2 > 59:
        return None

    return start, end


# =========================
# ENTRY POINT
# =========================
async def start_pt_sft_admin(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await reply(update, "❌ You are not authorised.")
        return

    context.user_data.clear()
    context.user_data["mode"] = "PT_SFT_ADMIN"

    await reply(
        update,
        "📋 *PT SFT Admin*\n\n"
        "Please enter SFT time range in 24H format.\n"
        "Example: `1500-1700`",
        parse_mode="Markdown",
    )


# =========================
# TEXT HANDLER
# =========================
async def handle_pt_sft_admin_text(update, context):
    if context.user_data.get("mode") != "PT_SFT_ADMIN":
        return

    result = _valid_time_range(update.message.text.strip())
    if not result:
        await reply(update, "❌ Invalid format. Use HHMM-HHMM (24H).")
        return

    start, end = result
    date = today_sg()

    set_sft_window(date, start, end)

    await reply(
        update,
        f"✅ *PT SFT window set*\n\n"
        f"Date: {date}\n"
        f"Time: {start}-{end}\n\n"
        f"Cadets may now submit SFT.",
        parse_mode="Markdown",
    )
