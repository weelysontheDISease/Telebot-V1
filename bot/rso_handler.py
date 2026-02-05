from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext
)

from config.constants import NAMES, instructor_list

from db.crud import get_user_records, update_user_record, create_user_record, get_ma_records, create_ma_record, update_ma_record

from helpers import reply

# def reply(update, text, reply_markup=None, parse_mode=None):  # Reusable reply function, change to put in ultils if needed elsewhere
#     if update.message:
#         update.message.reply_text(
#             text,
#             reply_markup=reply_markup,
#             parse_mode=parse_mode
#         )
#     else:
#         update.callback_query.edit_message_text(
#             text,
#             reply_markup=reply_markup,
#             parse_mode=parse_mode
#         )


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
            context.user_data['awaiting_mc_days'] = True
            reply(
                update,
                f"Diagnosis updated to: '{user_input.upper()}'"
            )
            show_mc_days_buttons(update, context)
            return

        if context.user_data.get("awaiting_custom_mc_days"):
            # Validate that input is a number
            try:
                mc_days = int(user_input)
                context.user_data['status'] = f"{mc_days} day(s) of MC"
                context.user_data['awaiting_custom_mc_days'] = False
                reply(
                    update,
                    f"Status updated to: '{context.user_data['status']}'"
                )
                show_preview_summary(update, context)
            except ValueError:
                reply(
                    update,
                    "Please enter a valid number for MC days."
                )
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
        context.user_data['record_id'] = latest_record.get('id')
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
    context.user_data['awaiting_mc_days'] = True

    reply(
        update,
        f"Diagnosis updated to: '{user_input.upper()}'"
    )
    show_mc_days_buttons(update, context)


def show_mc_days_buttons(update: Update, context: CallbackContext):
    """Show buttons for selecting MC days"""
    keyboard = [
        [InlineKeyboardButton("1 day", callback_data="mc_days|1")],
        [InlineKeyboardButton("2 days", callback_data="mc_days|2")],
        [InlineKeyboardButton("3 days", callback_data="mc_days|3")],
        [InlineKeyboardButton("4 days", callback_data="mc_days|4")],
        [InlineKeyboardButton("5 days", callback_data="mc_days|5")],
        [InlineKeyboardButton("Other", callback_data="mc_days|other")]
    ]
    reply(
        update,
        "How many days of MC have you gotten?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def mc_days_button_handler(update: Update, context: CallbackContext):
    """Handle MC days selection"""
    query = update.callback_query
    query.answer()

    _, days = query.data.split("|")

    if days == "other":
        context.user_data['awaiting_custom_mc_days'] = True
        reply(
            update,
            "Enter the number of MC days:"
        )
    else:
        context.user_data['status'] = f"{days} day(s) MC"
        context.user_data['awaiting_mc_days'] = False
        reply(
            update,
            f"Status updated to: '{context.user_data['status']}'"
        )
        show_preview_summary(update, context)


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
    diagnosis = context.user_data.get('diagnosis', None)
    status = context.user_data.get('status', None)

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
        record_id = context.user_data.get('record_id')
        update_user_record(
            record_id=record_id,
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

"""Report MA Handler Module"""

def start_ma_report(update: Update, context: CallbackContext):
    context.user_data.clear()  # Clear previous data
    context.user_data["mode"] = "ma_report"

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"name|{name}")]
        for name in NAMES
    ]
    reply(
        update,
        "Select your name for MA report:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def name_selection_handler_ma(update: Update, context: CallbackContext):  # manual input for MA appointment
    query = update.callback_query
    query.answer()
    key, name = query.data.split("|")
    if key == "name" and context.user_data.get("mode") == "ma_report":
        context.user_data['name'] = name
        context.user_data['awaiting_appointment'] = True
        reply(
            update,
            f"Name selected: {name}. Enter the name of your appointment.(E.g., Dental, Otolaryngology)",
        )


def manual_input_handler(update: Update, context: CallbackContext):
    if not update.message:
        return

    user_input = update.message.text.strip().upper()
    if not user_input:
        return

    # Handle MA appointment report flow
    if context.user_data.get("mode") == "ma_report":
        if context.user_data.get("awaiting_appointment"):
            context.user_data['appointment'] = user_input
            context.user_data['awaiting_appointment'] = False
            context.user_data['awaiting_location'] = True
            reply(
                update,
                f"Appointment recorded: {user_input}.\n\nPlease enter the location of your appointment."
            )
            return

        if context.user_data.get("awaiting_location"):
            context.user_data['appointment_location'] = user_input
            context.user_data['awaiting_location'] = False
            context.user_data['awaiting_date'] = True
            reply(
                update,
                f"Location recorded: {user_input}.\n\nPlease enter your appointment date in DDMMYY format."
            )
            return

        if context.user_data.get("awaiting_date"):
            context.user_data['appointment_date'] = user_input
            context.user_data['awaiting_date'] = False
            context.user_data['awaiting_time'] = True
            reply(
                update,
                f"Appointment date recorded: {user_input}.\n\nPlease enter your appointment time in HHMM and 24H format."
            )
            return

        if context.user_data.get("awaiting_time"):
            context.user_data['appointment_time'] = user_input
            context.user_data['awaiting_time'] = False
            reply(
                update,
                f"Appointment time recorded: {user_input}."
            )
            show_ma_preview_summary(update, context)
            return


def show_ma_preview_summary(update: Update, context: CallbackContext):
    name = context.user_data.get('name', 'N/A')
    appointment = context.user_data.get('appointment', 'N/A')
    appointment_location = context.user_data.get('appointment_location', 'N/A')
    appointment_date = context.user_data.get('appointment_date', 'N/A')
    appointment_time = context.user_data.get('appointment_time', 'N/A')

    summary = f"NAME: {name}\n"
    summary += f"NAME: {appointment}\n"
    summary += f"LOCATION: {appointment_location}\n"
    summary += f"DATE: {appointment_date}\n"
    summary += f"TIME OF APPOINTMENT: {appointment_time}\n"

    keyboard = [
        [
            InlineKeyboardButton("Confirm", callback_data="confirm_ma"),
            InlineKeyboardButton("Cancel", callback_data="cancel")
        ]
    ]
    reply(
        update,
        summary,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return

def confirm_ma_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query:
        return
    query.answer()

    name = context.user_data.get('name', 'N/A')
    appointment = context.user_data.get('appointment', 'N/A')
    appointment_location = context.user_data.get('appointment_location', 'N/A')
    appointment_date = context.user_data.get('appointment_date', 'N/A')
    appointment_time = context.user_data.get('appointment_time', 'N/A')

    # Save new MA report to database
    create_ma_record(
        name=name,
        appointment=appointment,
        appointment_location=appointment_location,
        appointment_date=appointment_date,
        appointment_time=appointment_time
    )

    reply(
        update,
        "MA Report saved. Thank you!"
    )
    context.user_data.clear()



def update_endorsed(update:Update, context:CallbackContext):
    """Start the update endorsed process - select name first"""
    context.user_data.clear()
    context.user_data["mode"] = "update_ma"

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"update_ma_name|{name}")]
        for name in NAMES
    ]
    reply(
        update,
        "Select your name to update MA endorsement:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def update_ma_name_selection_handler(update: Update, context: CallbackContext):
    """Handle name selection for MA update - check if records exist"""
    query = update.callback_query
    query.answer()

    _, name = query.data.split("|")
    context.user_data['name'] = name

    user_records = get_ma_records(name)

    # Filter ma_records for this specific person
    # user_records = [record for record in ma_records if record.get('name') == name]

    if not user_records:
        reply(
            update,
            f"No existing MA reports found for {name}."
        )
        context.user_data.clear()
        return
    else:
        # Pre-fill existing data from latest record
        latest_record = user_records[-1]  # Assuming the latest record is the last one
        context.user_data['appointment'] = latest_record.get('appointment', '')
        context.user_data['appointment_location'] = latest_record.get('appointment_location', '')
        context.user_data['appointment_date'] = latest_record.get('appointment_date', '')
        context.user_data['appointment_time'] = latest_record.get('appointment_time', '')

        keyboard = [
            [InlineKeyboardButton(instructor, callback_data=f"instructor|{instructor}")]
                for instructor in instructor_list
            ]
        reply(
                update,
                "Select who endorsed:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

def instructor_selection_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    key, instructor = query.data.split("|")
    if key == "instructor":
        context.user_data['instructor'] = instructor
        # Proceed to next step, e.g., ask for symptoms
        reply(
            update,
            f"Instructor selected: {instructor}.\n\n"
        )
        show_ma_update_summary(update, context)
        update_ma_record(
            name=context.user_data.get('name', 'N/A'),
            appointment=context.user_data.get('appointment', 'N/A'),
            appointment_location=context.user_data.get('appointment_location', 'N/A'),
            appointment_date=context.user_data.get('appointment_date', 'N/A'),
            appointment_time=context.user_data.get('appointment_time', 'N/A'),
            instructor=context.user_data.get('instructor', 'N/A')
        )

        return

def show_ma_update_summary(update: Update, context: CallbackContext):
    name = context.user_data.get('name', 'N/A')
    appointment = context.user_data.get('appointment', 'N/A')
    appointment_location = context.user_data.get('appointment_location', 'N/A')
    appointment_date = context.user_data.get('appointment_date', 'N/A')
    appointment_time = context.user_data.get('appointment_time', 'N/A')
    instructor = context.user_data.get('instructor', 'N/A')

    summary = f"NAME: {name}\n"
    summary += f"NAME: {appointment}\n"
    summary += f"LOCATION: {appointment_location}\n"
    summary += f"DATE: {appointment_date}\n"
    summary += f"TIME OF APPOINTMENT: {appointment_time}\n"
    summary += f"ENDORSED BY: {instructor}\n"

    reply(
        update,
        summary
    )
    return

def report_ma_command(update: Update, context: CallbackContext):
    start_ma_report(update, context)



