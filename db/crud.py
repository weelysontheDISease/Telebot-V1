from db.database import SessionLocal
from db.models import User, MovementLog

def get_user_by_telegram_id(telegram_id: int):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    finally:
        db.close()
