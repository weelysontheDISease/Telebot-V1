from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import BigInteger, Column, Integer, String, Boolean, Date, DateTime, Text
from datetime import datetime

class Base(DeclarativeBase):
    pass

# Schema for users table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    telegram_username = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    rank = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
# class Cadet(Base):
#     __tablename__ = 'cadets'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     rank = Column(String, nullable=False)
#     full_name = Column(String, nullable=False)
    
#     intake = Column(String, nullable=False)
#     expiry_date = Column(Date, nullable=False)
    
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
    
class MovementLog(Base):
    __tablename__ = "movement_logs"

    id = Column(Integer, primary_key=True)

    from_location = Column(String, nullable=False)
    to_location = Column(String, nullable=False)
    time = Column(String, nullable=False)  # HHMM

    created_by = Column(Integer, nullable=False)  # telegram_id
    created_at = Column(DateTime, default=datetime.utcnow)
    
class MedicalEvent(Base):
    __tablename__ = "medical_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # telegram_id

    event_type = Column(String, nullable=False) # MA / RSI / RSO / MC
    appointment_type = Column(String)
    location = Column(String)

    symptoms = Column(Text)
    diagnosis = Column(Text)

    endorsed_by = Column(String)

    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    
class MedicalStatus(Base):
    __tablename__ = "medical_statuses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)

    status_type = Column(String, nullable=False)  # MC / LD / EUL
    description = Column(String, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    source_event_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
