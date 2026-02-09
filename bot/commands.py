from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import os
import tempfile

from bot.helpers import reply
from config.constants import ACTIVITIES, ADMIN_IDS
from services.db_service import get_sft_window
from db.crud import clear_user_data, get_all_cadet_names
from db.import_users_csv import import_users

# =========================
# START ENTRY POINT
# =========================
async def start(update, context):
    context.user_data.clear()
    await reply(
        update,
        "👋 Welcome.\n\n"
        "Use /start_sft for SFT reporting or /start_movement for movement reporting."
    )


# =========================
# SFT ENTRY POINT
# =========================
async def start_sft(update, context):
    window = get_sft_window()

    if not window:
        await reply(
            update,
            "❌ PT SFT has not been opened by IC yet.\n"
            "Please wait for instructions."
        )
        return

    context.user_data.clear()
    context.user_data["mode"] = "SFT"
    context.user_data["start"] = window.start
    context.user_data["end"] = window.end
    context.user_data["date"] = window.date

    keyboard = [
        [
            InlineKeyboardButton(
                activity,
                callback_data=f"sft_activity|{activity}"
            )
        ]
        for activity in ACTIVITIES
    ]

    await reply(
        update,
        f"🏋️ *PT SFT Open*\n\n"
        f"Time: {window.start}-{window.end}\n\n"
        f"Select activity:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# MOVEMENT ENTRY POINT
# =========================
async def start_movement(update, context):
    context.user_data.clear()
    context.user_data["mode"] = "MOVEMENT"
    context.user_data["selected"] = set()
    names = get_all_cadet_names()
    context.user_data["all_names"] = names

    keyboard = [
        [
            InlineKeyboardButton(
                f"⬜ {name}",
                callback_data=f"mov:name|{name}"
            )
        ]
        for name in names
    ]

    keyboard.append(
        [InlineKeyboardButton("✅ Done Selecting", callback_data="mov:done")]
    )

    await reply(
        update,
        "🚶 *Movement reporting started*\n\nSelect personnel:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# STATUS REPORTING MENU
# =========================
async def start_status(update, context):
    """Main menu for RSO/MA/RSI reporting"""
    context.user_data.clear()

    keyboard = [
        [InlineKeyboardButton("📋 Report RSO", callback_data="status_menu|report_rso")],
        [InlineKeyboardButton("✏️ Update RSO", callback_data="status_menu|update_rso")],
        [InlineKeyboardButton("🏥 Report MA", callback_data="status_menu|report_ma")],
        [InlineKeyboardButton("✏️ Update MA", callback_data="status_menu|update_ma")],
        [InlineKeyboardButton("🤒 Report RSI", callback_data="status_menu|report_rsi")],
        [InlineKeyboardButton("✏️ Update RSI", callback_data="status_menu|update_rsi")],
        [InlineKeyboardButton("❌ Cancel", callback_data="status_menu|cancel")],
    ]

    await reply(
        update,
        "📊 *Status Reporting Menu*\n\nSelect an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# PARADE STATE ENTRY POINT
# =========================
async def start_parade_state(update, context):
	"""Entry point for parade state generation"""
	context.user_data.clear()
	context.user_data["mode"] = "PARADE_STATE"

	await reply(
		update,
		"📋Parade State started.\n\n"
		"Please input the number of out-of-camp personnel:"
	)
     

# =========================
# USER IMPORT (CSV)
# =========================
def _is_admin(user_id: int | None) -> bool:
    return user_id is not None and user_id in ADMIN_IDS


async def _handle_import_csv(update, context, clear_first: bool):
    document = update.message.document if update.message else None
    if not document:
        await reply(update, "❌ Please attach a CSV file for import.")
        return

    if not document.file_name or not document.file_name.lower().endswith(".csv"):
        await reply(update, "❌ Only .csv files are supported.")
        return

    if clear_first:
        cleared = clear_user_data()
        await reply(
            update,
            "🧹 Cleared existing data: "
            f"{cleared['users']} users, "
            f"{cleared['medical_events']} medical events, "
            f"{cleared['medical_statuses']} medical statuses.",
        )

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(tmp_path)
        try:
            result = import_users(tmp_path)
        except ValueError as exc:
            await reply(update, f"❌ Import failed: {exc}")
            return
        except Exception:
            await reply(update, "❌ Import failed due to an unexpected error.")
            return
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    await reply(
        update,
        "✅ Import complete. "
        f"Processed: {result['processed']}, "
        f"created: {result['created']}, "
        f"updated: {result['updated']}.",
    )



async def import_user(update, context):
    if not _is_admin(update.effective_user.id if update.effective_user else None):
        await reply(update, "❌ You are not authorized to use /import_user.")
        return

    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("📥 Import users (CSV)", callback_data="import_user|import")],
        [InlineKeyboardButton("👥 Display current users", callback_data="import_user|list")],
        [InlineKeyboardButton("🧹 Clear database", callback_data="import_user|clear")],
    ]
    await reply(
        update,
        "Choose an action:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def import_user_document(update, context):
    if context.user_data.get("mode") != "IMPORT_USER":
        return
    if not _is_admin(update.effective_user.id if update.effective_user else None):
        await reply(update, "❌ You are not authorized to import users.")
        return

    clear_first = bool(context.user_data.get("import_clear"))
    context.user_data.clear()
    await _handle_import_csv(update, context, clear_first)


async def import_user_callback(update, context):
    query = update.callback_query
    if not query:
        return
    await query.answer()

    if not _is_admin(update.effective_user.id if update.effective_user else None):
        await reply(update, "❌ You are not authorized to manage imports.")
        return

    _, action = query.data.split("|", 1)

    if action == "import":
        context.user_data.clear()
        context.user_data["mode"] = "IMPORT_USER"
        context.user_data["import_clear"] = False
        await reply(update, "📥 Send the CSV file to import users.")
        return

    if action == "list":
        users = list_users()
        if not users:
            await reply(update, "No users found.")
            return
        lines = ["Current users:"]
        for user in users:
            admin_flag = " (admin)" if user.is_admin else ""
            lines.append(f"- {user.rank} {user.full_name} [{user.role}]{admin_flag}")
        if len(users) >= 200:
            lines.append("")
            lines.append("Showing first 200 users.")
        await reply(update, "\n".join(lines))
        return

    if action == "clear":
        keyboard = [
            [InlineKeyboardButton("✅ Confirm clear", callback_data="import_user|confirm_clear")],
            [InlineKeyboardButton("❌ Cancel", callback_data="import_user|cancel")],
        ]
        await reply(
            update,
            "This will delete all users and medical records. Are you sure?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if action == "confirm_clear":
        cleared = clear_user_data()
        await reply(
            update,
            "🧹 Cleared existing data: "
            f"{cleared['users']} users, "
            f"{cleared['medical_events']} medical events, "
            f"{cleared['medical_statuses']} medical statuses.",
        )
        return

    if action == "cancel":
        context.user_data.clear()
        await reply(update, "Cancelled.")