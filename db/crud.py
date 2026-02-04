from db.database import SessionLocal
from db.models import MedicalEvent, MedicalStatus, User, MovementLog

db = SessionLocal()

def get_user_by_telegram_id(telegram_id: int):
    try:
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    finally:
        db.close()
        
# Movement

def create_medical_event(user_id, event_type, **kwargs):
    event = MedicalEvent(user_id=user_id, event_type=event_type, **kwargs)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def get_medical_event(today):
    return db.query(MedicalEvent).filter(
        MedicalEvent.start_datetime <= today,
        MedicalEvent.end_datetime >= today
    ).all()

def get_active_statuses(today):
    return db.query(MedicalStatus).filter(
        MedicalStatus.start_date <= today,
        MedicalStatus.end_date >= today
    ).all()