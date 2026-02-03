from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import BigInteger, Column, Integer, String, Boolean, Date, DateTime, Text
from datetime import datetime

class Base(DeclarativeBase):
    pass

# Schema for users table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    telegram_username = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    rank = Column(String, nullable=True)
    role = Column(String, nullable=False)
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
