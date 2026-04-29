from sqlalchemy import Index, Integer, String, Boolean, DateTime, Text
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from utils.time import utc_now


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    created_by: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    room: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(20), default="text", nullable=False
    )
    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    reply_to_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    __table_args__ = (Index("ix_messages_room_id", "room", "id"),)
