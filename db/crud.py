from datetime import date, datetime, time
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import MedicalEvent, MedicalStatus, User

db = SessionLocal()

# ---------- Users ----------

db = SessionLocal()

def get_user_by_telegram_id(telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def _normalize_username(value: str | None):
    if value is None:
        return None
    name = value.strip()
    if not name:
        return None
    if name.startswith("@"):
        name = name[1:]
    return name or None


def create_user(
    full_name: str,
    rank: str,
    role: str,
    telegram_id: int | None = None,
    telegram_username: str | None = None,
    is_admin: bool = False,
    is_active: bool = True,
):
    telegram_username = _normalize_username(telegram_username)
    if telegram_id is None and not telegram_username:
        raise ValueError("telegram_id or telegram_username is required")

    if telegram_id is not None:
        existing = db.query(User).filter(User.telegram_id == telegram_id).first()
        if existing:
            raise ValueError("telegram_id already exists")
    if telegram_username:
        existing = db.query(User).filter(User.telegram_username == telegram_username).first()
        if existing:
            raise ValueError("telegram_username already exists")

    user = User(
        telegram_id=telegram_id,
        telegram_username=telegram_username,
        full_name=full_name,
        rank=rank,
        role=role,
        is_admin=is_admin,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ---------- Medical ----------

def create_medical_event(
    user_id: int,
    event_type: str,
    symptoms: str,
    diagnosis: str,
    event_date: date | None = None,
    event_time: time | None = None,
):
    if event_date is None or event_time is None:
        now = datetime.now()
        event_date = event_date or now.date()
        event_time = event_time or now.time().replace(microsecond=0)
    event = MedicalEvent(
        user_id=user_id,
        event_type=event_type,
        symptoms=symptoms,
        diagnosis=diagnosis,
        event_date=event_date,
        event_time=event_time,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def create_medical_status(
    user_id: int,
    status_type: str,
    description: str,
    start_date,
    end_date
):
    status = MedicalStatus(
        user_id=user_id,
        status_type=status_type,
        description=description,
        start_date=start_date,
        end_date=end_date
    )
    db.add(status)
    db.commit()
    db.refresh(status)
    return status

def get_active_statuses(target_date: date):
    """Retrieve all medical statuses active on the target_date."""
    return db.query(MedicalStatus).filter(
        MedicalStatus.start_date <= target_date,
        MedicalStatus.end_date >= target_date
    ).all()

def get_medical_events():
    return db.query(
        MedicalEvent,
        User
	).join(
		User, MedicalEvent.user_id == User.id
    ).all()

def get_active_statuses(today):
    return db.query(
        MedicalStatus,
        User
        ).join(
            User, MedicalStatus.user_id == User.id
		).filter(
        MedicalStatus.start_date <= today,
        MedicalStatus.end_date >= today
    ).all()

def get_all_cadets():
    return db.query(User).filter(
        User.role == "Cadet"
	).all()