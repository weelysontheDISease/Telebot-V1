from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext
)

from config.constants import NAMES

from db.crud import get_user_records, update_user_record, create_user_record

def reply(update, text, reply_markup=None, parse_mode=None):  # Reusable reply function, change to put in ultils if needed elsewhere
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


# def get_records(database_service, name):
#     """Fetch user records from the database"""
#     records = database_service.get_user_records(name)
#     return records

def start_status_report(update: Update, context: CallbackContext):
    context.user_data.clear()  # Clear previous data
    context.user_data["mode"] = "report"

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"name|{name}")]
        for name in NAMES
    ]
    reply(
        update,
        "Select your name:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def name_selection_handler(update: Update, context: CallbackContext):  # manual input for symptoms
    query = update.callback_query
    query.answer()
    key, name = query.data.split("|")
    if key == "name":
        context.user_data['name'] = name
        context.user_data['symptoms'] = []
        context.user_data['awaiting_symptoms'] = True
        # Proceed to next step, e.g., ask for symptoms
        reply(
            update,
            f"Name selected: {name}.Describe your symptoms.",
        )

def manual_input_handler(update: Update, context: CallbackContext):
    if not update.message:
        return

    user_input = update.message.text.strip()
    if not user_input:
        return

    if context.user_data.get("mode") == "report":
        if context.user_data.get("awaiting_symptoms"):
            context.user_data['symptoms'].append(user_input.upper())
            context.user_data['awaiting_symptoms'] = False
            context.user_data['awaiting_diagnosis'] = True
            reply(
                update,
                f"Symptom recorded: {user_input.upper()}.\n\nPlease enter your diagnosis."
            )
            show_preview_summary(update, context)
            return

        # if context.user_data.get("awaiting_diagnosis"):
        #     context.user_data['diagnosis'] = user_input.upper()
        #     context.user_data['awaiting_diagnosis'] = False
        #     context.user_data['awaiting_status'] = True
        #     reply(
        #         update,
        #         f"Diagnosis recorded: {user_input.upper()}.\n\nPlease enter your medical status."
        #     )
        #     return

        # if context.user_data.get("awaiting_status"):
        #     context.user_data['status'] = user_input.upper()
        #     context.user_data['awaiting_status'] = False
        #     reply(
        #         update,
        #         f"Status recorded: {user_input.upper()}."
        #     )
        #     show_preview_summary(update, context)
        #     return

    if context.user_data.get("mode") == "update":
        if context.user_data.get("awaiting_diagnosis"):
            context.user_data['diagnosis'] = user_input.upper()
            context.user_data['awaiting_diagnosis'] = False
            context.user_data['awaiting_status'] = True
            reply(
                update,
                f"Diagnosis updated to: '{user_input.upper()}'\n\nNow, please enter your medical status :"
            )
            return

        if context.user_data.get("awaiting_status"):
            context.user_data['status'] = user_input.upper()
            context.user_data['awaiting_status'] = False
            reply(
                update,
                f"Status updated to: '{user_input.upper()}'"
            )
            show_preview_summary(update, context)
            return


def start_update_status(update: Update, context: CallbackContext):
    """Start the update process - get user name to find their report"""
    context.user_data.clear()
    context.user_data["mode"] = "update"

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"update_name|{name}")]
        for name in NAMES
    ]

    reply(
        update,
        "Select your name to update your status report:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def update_name_selection_handler(update: Update, context: CallbackContext):
    """Handle name selection for update"""
    query = update.callback_query
    query.answer()

    _, name = query.data.split("|")
    context.user_data['name'] = name
    context.user_data['updating'] = True
    context.user_data['awaiting_diagnosis'] = True

    # Here you would typically fetch the existing report from database
    records = get_user_records(name)
    if not records:
        reply(
            update,
            f"No existing report found for {name}. Please use /report_sick to create a new report."
        )
        context.user_data.clear()
        return
    else:
        # Pre-fill existing data
        latest_record = records[-1]  # Assuming the latest record is the last one
        context.user_data['symptoms'] = latest_record.get('symptoms', [])
        context.user_data['diagnosis'] = latest_record.get('diagnosis', '')
        context.user_data['status'] = latest_record.get('status', '')
        reply(
            update,
            f"Updating report for {name}. What is your diagnosis?"
        )

def update_input_handler(update: Update, context: CallbackContext):
    """Handle input for updating fields"""
    if not update.message:
        return

    user_input = update.message.text.strip()
    if not user_input:
        return

    context.user_data['diagnosis'] = user_input.upper()
    context.user_data['awaiting_status'] = True

    reply(
        update,
        f"Diagnosis updated to: '{user_input.upper()}'\n\nNow, please enter your medical status :"
    )


def show_preview_summary(update: Update, context: CallbackContext):
    name = context.user_data.get('name', 'N/A')
    symptoms = context.user_data.get('symptoms', [])
    diagnosis = context.user_data.get('diagnosis', '')
    status = context.user_data.get('status', '')

    summary = f"NAME: {name}\n"
    summary += f"SYMPTOMS: {', '.join(symptoms) if symptoms else 'N/A'}\n"
    summary += f"DIAGNOSIS: {diagnosis}\n"
    summary += f"STATUS: {status}\n"

    keyboard = [
        [
            InlineKeyboardButton("Confirm", callback_data="confirm"),
            InlineKeyboardButton("Cancel", callback_data="cancel")
        ]
    ]
    reply(
        update,
        summary,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return


def confirm_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query:
        return
    query.answer()

    name = context.user_data.get('name', 'N/A')
    symptoms = context.user_data.get('symptoms', [])
    diagnosis = context.user_data.get('diagnosis', '')
    status = context.user_data.get('status', '')

    if context.user_data.get("mode") == "report":
        # Save new report to database
        create_user_record(
            name=name,
            symptoms=symptoms,
            diagnosis=diagnosis,
            status=status
        )

        # Add logic to send to IC Chat
    elif context.user_data.get("mode") == "update":
        # Update existing report in database
        update_user_record(
            name=name,
            symptoms=symptoms,
            diagnosis=diagnosis,
            status=status
        )

        # Add logic to send update to IC Chat

    reply(
        update,
        "Report saved. Thank you!"
    )
    context.user_data.clear()


def cancel(update: Update, context: CallbackContext):
    context.user_data.clear()
    reply(update, "Cancelled.")


def report_sick_command(update: Update, context: CallbackContext):
    start_status_report(update, context)


def update_sick_command(update: Update, context: CallbackContext):
    start_update_status(update, context)


def start_command(update: Update, context: CallbackContext):
    reply(
        update,
        "Welcome. Use /report_sick to submit a report or /update_sick to update one."
    )

