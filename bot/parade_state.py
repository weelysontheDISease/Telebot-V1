from datetime import datetime
from db import crud


def categorise_medical_events(events):
	"""Categorise medical events as MA, RSI or RSO"""
	rso_events = []
	rsi_events = []
	mc_events = []
	ma_events = []

	for event in events:
		if event[0].event_type == "RSO":
			rso_events.append(event)
		elif event[0].event_type == "RSI":
			rsi_events.append(event)
		elif event[0].event_type == "MC":
			mc_events.append(event)
		elif event[0].event_type == "MA":
			ma_events.append(event)
		else:
			print("Unsupported event_type. Only RSO, RSI, MC or MA.")

	categorised_medical_events = {"rsi": rsi_events, "rso": rso_events, "mc": mc_events, "ma": ma_events}
	return categorised_medical_events

def format_rso_rsi(events):
	final_text = ""
	for i, event in enumerate(events):
		medical_event = event[0]
		user = event[1]

		final_text += f"""
{i+1}. {user.rank} {user.full_name}
SYMPTOMS: {medical_event.symptoms}
DIAGNOSIS: 
STATUS: 
"""
		return final_text

def format_mc(events):
	final_text = ""
	for i, event in enumerate(events):
		medical_event = event[0]
		user = event[1]

		mc_start = medical_event.start_datetime
		mc_end = medical_event.end_datetime
		mc_duration = mc_end - mc_start
		mc_start_date = mc_start.strftime("%d%m%y")
		mc_end_date = mc_end.strftime("%d%m%y")
		mc_duration_days = mc_duration.days

		final_text += f"""
{i+1}. {user.rank} {user.full_name}
SYMPTOMS: {medical_event.symptoms}
DIAGNOSIS: {medical_event.diagnosis}
STATUS: {mc_duration_days} DAYS MC ({mc_start_date}-{mc_end_date})
"""
	return final_text

		
def format_ma(events):
	final_text = ""
	for i, event in enumerate(events):
		medical_event = event[0]
		user = event[1]

		final_text += f"""
{i+1}. {user.rank} {user.full_name}
a. NAME: {medical_event.appointment_type}
LOCATION: {medical_event.location}
DATE: {medical_event.end_datetime}
TIME OF APPOINTMENT: {medical_event.end_datetime}
ENDORSED BY: {medical_event.endorsed_by}
"""

def generate_parade_state(update, context):
	"""Generates the current parade state"""
	current_datetime = datetime.now()
	current_time = current_datetime.time().strftime('%H%M')
	current_date = current_datetime.date().strftime('%d%m%y')

	all_medical_events = crud.get_medical_events(current_datetime)
	all_cadets = crud.get_all_cadets()

	categorised_medical_events = categorise_medical_events(all_medical_events)

	rso_count = len(categorised_medical_events["rso"])
	rsi_count = len(categorised_medical_events["rsi"])
	mc_count = len(categorised_medical_events["mc"])
	ma_count = len(categorised_medical_events["ma"])
	
	if rso_count > 0:
		rso_text = format_rso_rsi(categorised_medical_events["rso"])
	else:
		rso_text = ""
	
	if rsi_count > 0:
		rsi_text = format_rso_rsi(categorised_medical_events["rsi"])
	else:
		rsi_text = ""

	if mc_count > 0:
		mc_text = format_mc(categorised_medical_events["mc"])

	if ma_count > 0:
		ma_text = format_ma(categorised_medical_events["ma"])
	else:
		ma_text = ""

	others_text = status_text = permstatus_text = "XX" 
	others_count = status_count = permstatus_count = 0

	# if MA dates include today, out_of_camp_ma_count += 1
	out_of_camp = 0
	# out_of_camp = rso_count + mc_count + out_of_camp_ma_count
	
	total_strength = len(all_cadets)
	current_strength = total_strength - out_of_camp
	
	parade_state_text = f"""
DIS WING 14/26 PRE-MDST PARADE STATE {current_date}, {current_time}H
-------------------------------------------------------- 

TOTAL STRENGTH: {total_strength}

CURRENT STRENGTH: {current_strength}
OUT OF CAMP: {out_of_camp}

-------------------------------------------------------- 

MA: {ma_count:02d}
{ma_text}

-------------------------------------------------------- 

RSI : {rsi_count:02d}
{rsi_text}

RSO : {rso_count:02d}
{rso_text}

-------------------------------------------------------- 

MC: {mc_count:02d}
{mc_text}

-------------------------------------------------------- 

OTHERS: {others_count:02d}
{others_text}

--------------------------------------------------------

STATUSES: {status_count:02d}
{status_text}


PERMANENT STATUS: {permstatus_count:02d}
{permstatus_text}
"""
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=parade_state_text
	)
