from datetime import datetime, date
from typing import Optional, Literal, List
from pydantic import BaseModel, EmailStr, Field


# =========================================================
# USERS
# =========================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    token: str
    user: UserResponse


# =========================================================
# SESSIONS
# =========================================================

class SessionCreateRequest(BaseModel):
    """
    ❗ user_id REMOVED
    User is resolved from JWT
    """
    title: Optional[str] = "New Conversation"


class SessionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


# =========================================================
# CHAT
# =========================================================

class ChatRequest(BaseModel):
    """
    ❗ user_id REMOVED
    Derived from JWT
    """
    session_id: int = Field(..., gt=0)
    message: str = Field(..., min_length=1, max_length=5000)


class ChatMessage(BaseModel):
    """
    API response format
    DB: Message.text → API: content
    """
    id: int
    session_id: int
    user_id: int
    role: Literal["user", "assistant"]
    content: str
    emotion: Optional[str] = None
    loneliness_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """
    Single, clean response contract
    """
    reply: str
    emotion: Optional[str] = None
    loneliness_score: Optional[float] = None
    is_fallback: bool = False
    is_crisis_response: bool = False
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UpdateMessageRequest(BaseModel):
    """
    Used for edit + regenerate
    """
    content: str = Field(..., min_length=1, max_length=5000)


class ChatHistoryResponse(BaseModel):
    session_id: int
    messages: List[ChatMessage]
    drift_score: Optional[float] = None
    status: Optional[str] = None


class CalendarDayResponse(BaseModel):
    date: date
    dominant_emotion: str
    avg_loneliness: Optional[float]
    message_count: int


class WeeklyEmotionResponse(BaseModel):
    date: str
    avg_loneliness: Optional[float]
    message_count: int
