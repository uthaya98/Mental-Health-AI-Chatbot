from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Float,
    Text,
    UniqueConstraint,
    Date
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, date

Base = declarative_base()


# =========================================================
# USER TABLE
# =========================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True, nullable=False)  # ADDED
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,  # Changed from user_id to id for consistency
            "username": self.username,  # ADDED
            "email": self.email,
            "created_at": self.created_at,
        }


# =========================================================
# SESSION TABLE
# =========================================================
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, default="New Conversation")  # Changed default title

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,  # Changed from session_id to id
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# =========================================================
# MESSAGE TABLE
# =========================================================
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Message info
    role = Column(String)  # "user" or "assistant"
    content = Column(Text, nullable=False)  # Changed from 'text' to 'content' to match frontend
    emotion = Column(String, nullable=True)
    loneliness_score = Column(Float, nullable=True)

    # Soft-delete for editing/regeneration
    deleted = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    session = relationship("Session", back_populates="messages")
    user = relationship("User", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "role": self.role,
            "content": self.content,  # Changed from 'text' to 'content'
            "emotion": self.emotion,
            "loneliness_score": self.loneliness_score,
            "deleted": self.deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
class DailyEmotionSummary(Base):
    __tablename__ = "daily_emotion_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    dominant_emotion = Column(String, nullable=False)
    avg_loneliness = Column(Float, nullable=True)
    message_count = Column(Integer, default=0)

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "dominant_emotion": self.dominant_emotion,
            "avg_loneliness": self.avg_loneliness,
            "message_count": self.message_count,
        }
