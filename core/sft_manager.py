from datetime import datetime
import pytz

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.helpers import reply
from services.user_service import UserService
from services.db_service import SFTService
from config.constants import IC_GROUP_CHAT_ID, SFT_TOPIC_ID, SFT_ACTIVITIES

SG_TZ = pytz.timezone("Asia/Singapore")


def today_sg():
    return datetime.now(SG_TZ).strftime("%d%m%Y")


def handle_sft_callback(update, context):
    query = update.callback_query
    query.answer()
    data = query.data

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

        reply(update, "Select START time:", InlineKeyboardMarkup(keyboard))

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

        reply(update, "Select END time:", InlineKeyboardMarkup(keyboard))

    # ------------------------------
    # END TIME → SAVE
    # ------------------------------
    elif data.startswith("sft_end|"):
        context.user_data["end"] = data.split("|")[1]

        user = UserService.require_user(update.effective_user)

        SFTService.add_submission(
            user_id=user.telegram_id,
            user_name=user.full_name,
            activity=context.user_data["activity"],
            location=context.user_data["location"],
            start=context.user_data["start"],
            end=context.user_data["end"],
            date=today_sg(),
        )

        reply(
            update,
            f"✅ *SFT Submitted*\n\n"
            f"{user.full_name}\n"
            f"{context.user_data['activity']} @ {context.user_data['location']}\n"
            f"{context.user_data['start']}-{context.user_data['end']}",
            parse_mode="Markdown",
        )

    # ------------------------------
    # ADMIN: GENERATE SUMMARY
    # ------------------------------
    elif data == "sft_generate":
        UserService.require_admin(update.effective_user.id)

        report = SFTService.generate_summary(today_sg())
        context.user_data["final_message"] = report

        keyboard = [[
            InlineKeyboardButton("✅ Confirm & Send", callback_data="sft_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="sft_cancel"),
        ]]

        reply(
            update,
            "📋 *Preview SFT Summary*\n\n" + report,
            InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    # ------------------------------
    # CONFIRM SEND
    # ------------------------------
    elif data == "sft_confirm":
        UserService.require_admin(update.effective_user.id)

        context.bot.send_message(
            chat_id=IC_GROUP_CHAT_ID,
            message_thread_id=SFT_TOPIC_ID,
            text=context.user_data["final_message"],
        )

        reply(update, "✅ SFT summary sent.")

    # ------------------------------
    # CANCEL
    # ------------------------------
    elif data == "sft_cancel":
        reply(update, "❌ SFT summary cancelled.")
