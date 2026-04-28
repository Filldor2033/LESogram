from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    is_admin = Column(Boolean, nullable=False, default=False, server_default="0", index=True)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_by = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    room = Column(String(100), nullable=False, index=True)
    text = Column(String(1000), nullable=False, default="")
    content_type = Column(String(20), nullable=False, default="text")
    media_url = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    mime_type = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
