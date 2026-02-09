from datetime import datetime
import pytz

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers import reply
from services.db_service import SFTService
from db.crud import get_user_by_telegram_id
from config.constants import ACTIVITIES

SG_TZ = pytz.timezone("Asia/Singapore")


def today_sg():
    return datetime.now(SG_TZ).strftime("%d%m%Y")


# =========================
# SFT CALLBACK HANDLER
# =========================
async def handle_sft_callbacks(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    telegram_id = update.effective_user.id

    # ------------------------------
    # Resolve user from DB ONCE
    # ------------------------------
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        await reply(
            update,
            "❌ You are not registered in the system.\n"
            "Please contact the administrator."
        )
        return

    # Cache user identity
    context.user_data["user_id"] = user.id
    context.user_data["user_name"] = user.full_name

    # ------------------------------
    # ACTIVITY SELECTION
    # ------------------------------
    if data.startswith("sft_activity|"):
        activity, location = data.split("|")[1:]
        context.user_data["activity"] = activity
        context.user_data["location"] = location

        times = context.user_data["time_options"]
        keyboard = [
            [InlineKeyboardButton(t, callback_data=f"sft_start|{t}")]
            for t in times
        ]

        await reply(update, "Select START time:", InlineKeyboardMarkup(keyboard))

    # ------------------------------
    # START TIME
    # ------------------------------
    elif data.startswith("sft_start|"):
        context.user_data["start"] = data.split("|")[1]

        times = [
            t for t in context.user_data["time_options"]
            if t > context.user_data["start"]
        ]

        keyboard = [
            [InlineKeyboardButton(t, callback_data=f"sft_end|{t}")]
            for t in times
        ]

        await reply(update, "Select END time:", InlineKeyboardMarkup(keyboard))

    # ------------------------------
    # END TIME → PREVIEW
    # ------------------------------
    elif data.startswith("sft_end|"):
        context.user_data["end"] = data.split("|")[1]

        preview = (
            f"📋 *SFT Submission Preview*\n\n"
            f"{user.full_name}\n"
            f"{context.user_data['activity']} @ {context.user_data['location']}\n"
            f"{context.user_data['start']}-{context.user_data['end']}"
        )

        keyboard = [[
            InlineKeyboardButton("✅ Confirm & Submit", callback_data="sft_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="sft_cancel"),
        ]]

        await reply(update, preview, InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    # ------------------------------
    # CONFIRM SUBMISSION
    # ------------------------------
    elif data == "sft_confirm":
        SFTService.add_submission(
            user_id=context.user_data["user_id"],     # DB user ID
            user_name=context.user_data["user_name"], # snapshot
            activity=context.user_data["activity"],
            location=context.user_data["location"],
            start=context.user_data["start"],
            end=context.user_data["end"],
            date=today_sg(),
        )

        await reply(update, "✅ SFT successfully submitted.")

    # ------------------------------
    # CANCEL
    # ------------------------------
    elif data == "sft_cancel":
        context.user_data.clear()
        await reply(update, "❌ SFT submission cancelled.")
