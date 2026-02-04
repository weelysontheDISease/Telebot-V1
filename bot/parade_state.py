from datetime import datetime
from db import crud

total_strength = 22  # Modify if total strength changes

def retrieve_medical_events():
	current_time = datetime.now()
	medical_events = crud.get_medical_event(current_time)

	return medical_events

def generate_parade_state(update, context):
	"""Generates the current parade state"""
	current_datetime = datetime.now()
	current_time = current_datetime.time().strftime('%H%M')
	current_date = current_datetime.date().strftime('%d%m%y')

	total_strength = current_strength = out_of_camp = ma_count = ma_text = rsi_count = rsi_text = rso_count = rso_text = mc_count = mc_text = others_count = others_text = status_count = status_text = permstatus_count = permstatus_text = "XX" 
	# get strength from database here
	
	parade_state_text = f"""
DIS WING 14/26 PRE-MDST PARADE STATE {current_date}, {current_time}H
-------------------------------------------------------- 

TOTAL STRENGTH: {total_strength}

CURRENT STRENGTH: {current_strength}
OUT OF CAMP: {out_of_camp}

-------------------------------------------------------- 

MA: {ma_count}
{ma_text}

-------------------------------------------------------- 

RSI : {rsi_count}
{rsi_text}

RSO : {rso_count}
{rso_text}

-------------------------------------------------------- 

MC: {mc_count}
{mc_text}

-------------------------------------------------------- 

OTHERS: {others_count}
{others_text}

--------------------------------------------------------

STATUSES: {status_count}
{status_text}


PERMANENT STATUS: {permstatus_count}
{permstatus_text}
"""
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=parade_state_text
	)
