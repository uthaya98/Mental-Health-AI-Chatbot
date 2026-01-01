from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, extract, desc
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, date
from typing import Optional, List
from app.services.llm import generate_response

from app.db.models import User, Session, Message, DailyEmotionSummary


# =========================================================
# USERS
# =========================================================

async def create_user(
    db: AsyncSession, 
    username: str,  # ADDED
    email: str, 
    password_hash: str
) -> dict:
    """Create a new user with username, email, and password"""
    
    # Check if username already exists
    existing_username = await db.execute(
        select(User).where(User.username == username)
    )
    if existing_username.scalar_one_or_none():
        raise ValueError("Username already registered")
    
    # Check if email already exists
    existing_email = await db.execute(
        select(User).where(User.email == email)
    )
    if existing_email.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        username=username,  # ADDED
        email=email,
        password_hash=password_hash,
        created_at=datetime.utcnow()
    )

    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user.to_dict()
    except IntegrityError as e:
        await db.rollback()
        if "username" in str(e).lower():
            raise ValueError("Username already registered")
        elif "email" in str(e).lower():
            raise ValueError("Email already registered")
        else:
            raise ValueError("User already exists")


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[dict]:
    """Get user by username - ADDED for login"""
    r = await db.execute(select(User).where(User.username == username))
    user = r.scalar_one_or_none()
    if not user:
        return None
    
    # Return with password_hash for login verification
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "password_hash": user.password_hash,
        "created_at": user.created_at
    }


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[dict]:
    """Get user by email"""
    r = await db.execute(select(User).where(User.email == email))
    user = r.scalar_one_or_none()
    if not user:
        return None
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "password_hash": user.password_hash,
        "created_at": user.created_at
    }


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[dict]:
    """Get user by ID"""
    r = await db.execute(select(User).where(User.id == user_id))
    user = r.scalar_one_or_none()
    return user.to_dict() if user else None


# =========================================================
# SESSIONS
# =========================================================

async def create_session(db: AsyncSession, user_id: int, title: str) -> dict:
    session = Session(
        user_id=user_id,
        title=title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "id": session.id,
        "user_id": session.user_id,
        "title": session.title,
        "created_at": session.created_at
    }


async def get_session(db: AsyncSession, session_id: int) -> Optional[dict]:
    """Get a session by ID"""
    r = await db.execute(select(Session).where(Session.id == session_id))
    session = r.scalar_one_or_none()
    return session.to_dict() if session else None


async def get_sessions_by_user(db: AsyncSession, user_id: int) -> List[dict]:
    """Get all sessions for a user, ordered by most recent"""
    r = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(Session.updated_at.desc())
    )
    return r.scalars().all()


async def update_session_activity(db: AsyncSession, session_id: int) -> bool:
    """Update session's last activity timestamp"""
    r = await db.execute(
        update(Session)
        .where(Session.id == session_id)
        .values(updated_at=datetime.utcnow())
    )
    await db.commit()
    return r.rowcount > 0


async def delete_session(db: AsyncSession, session_id: int) -> bool:
    """Delete a session and all its messages"""
    # Delete all messages in the session first
    await db.execute(delete(Message).where(Message.session_id == session_id))

    # Delete the session
    r = await db.execute(delete(Session).where(Session.id == session_id))
    await db.commit()

    return r.rowcount > 0


# =========================================================
# MESSAGES
# =========================================================

async def create_message(
    db: AsyncSession,
    session_id: int,
    user_id: int,
    role: str,
    content: str,
    emotion: str | None,
    loneliness_score: float | None
):
    msg = Message(
        session_id=session_id,
        user_id=user_id,
        role=role,
        content=content,   # ✅ CORRECT
        emotion=emotion,
        loneliness_score=loneliness_score
    )

    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg.to_dict()



async def get_messages_by_session(
    db: AsyncSession,
    session_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[dict]:
    """Get all non-deleted messages in a session"""
    r = await db.execute(
        select(Message)
        .where(
            Message.session_id == session_id,
            Message.deleted == False
        )
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    return [m.to_dict() for m in r.scalars().all()]


async def get_messages_for_session(
    db: AsyncSession,
    session_id: int
) -> List[dict]:
    """Return ALL non-deleted messages for a session (ordered)"""
    r = await db.execute(
        select(Message)
        .where(Message.session_id == session_id, Message.deleted == False)
        .order_by(Message.created_at.asc())
    )
    return [m.to_dict() for m in r.scalars().all()]


# =========================================================
# MESSAGE EDITING RULE SUPPORT
# =========================================================

async def get_last_user_message(db: AsyncSession, session_id: int) -> Optional[dict]:
    """Returns latest non-deleted USER message"""
    r = await db.execute(
        select(Message)
        .where(
            Message.session_id == session_id,
            Message.role == "user",
            Message.deleted == False
        )
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    msg = r.scalar_one_or_none()
    return msg.to_dict() if msg else None


async def is_latest_user_message(db: AsyncSession, session_id: int, message_id: int) -> bool:
    """Check if message_id is the latest user message"""
    last = await get_last_user_message(db, session_id)
    return last and last["id"] == message_id


async def get_last_message(db: AsyncSession, session_id: int) -> Optional[dict]:
    """Return latest message (user or assistant)"""
    r = await db.execute(
        select(Message)
        .where(
            Message.session_id == session_id,
            Message.deleted == False
        )
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    msg = r.scalar_one_or_none()
    return msg.to_dict() if msg else None


async def get_message_by_id(db: AsyncSession, message_id: int) -> Optional[dict]:
    """Get a single message by ID"""
    r = await db.execute(
        select(Message).where(Message.id == message_id, Message.deleted == False)
    )
    msg = r.scalar_one_or_none()
    return msg.to_dict() if msg else None


async def update_message_text(
    db: AsyncSession,
    message_id: int,
    new_content: str  # CHANGED from 'new_text' to 'new_content'
) -> Optional[dict]:
    """Update message content for latest-editable user messages"""
    r = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.deleted == False
        )
    )
    msg = r.scalar_one_or_none()
    if not msg:
        return None

    msg.content = new_content  # CHANGED from 'text' to 'content'
    msg.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(msg)
    return msg.to_dict()


async def update_message(
    db: AsyncSession,
    message_id: int,
    new_content: str  # CHANGED from 'new_text' to 'new_content'
) -> Optional[dict]:
    """Update a message's content"""
    result = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.deleted == False
        )
    )
    msg = result.scalar_one_or_none()
    if not msg:
        return None

    msg.content = new_content  # CHANGED from 'text' to 'content'
    msg.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(msg)
    return msg.to_dict()


async def update_message_in_session(
    db: AsyncSession,
    session_id: int,
    message_id: int,
    user_id: int,
    new_content: str  # CHANGED from 'new_text' to 'new_content'
) -> Optional[dict]:
    """Update a message inside a specific session with edit rules applied"""

    # 1️⃣ Fetch message
    r = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.deleted == False
        )
    )
    msg = r.scalar_one_or_none()
    if not msg:
        return None

    # 2️⃣ Validate session ownership
    if msg.session_id != session_id:
        raise ValueError("Message does not belong to this session.")

    # 3️⃣ Validate user ownership
    if msg.user_id != user_id:
        raise ValueError("You can only edit your own messages.")

    # 4️⃣ Ensure this is LAST user message
    last_user_msg = await get_last_user_message(db, session_id)
    if not last_user_msg or last_user_msg["id"] != message_id:
        raise ValueError("Only the latest user message can be edited.")

    # 5️⃣ Update the message
    msg.content = new_content  # CHANGED from 'text' to 'content'
    msg.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(msg)

    return msg.to_dict()


async def soft_delete_message(db: AsyncSession, message_id: int) -> bool:
    """Soft delete a message (mark as deleted)"""
    r = await db.execute(
        update(Message)
        .where(Message.id == message_id)
        .values(
            deleted=True,
            updated_at=datetime.utcnow()
        )
    )
    await db.commit()
    return r.rowcount > 0


async def delete_message(db: AsyncSession, message_id: int) -> bool:
    """Soft delete a message"""
    result = await db.execute(
        update(Message)
        .where(Message.id == message_id)
        .values(deleted=True, updated_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount > 0


async def hard_delete_message(db: AsyncSession, message_id: int) -> bool:
    """Permanently delete a message (used for regeneration)"""
    r = await db.execute(delete(Message).where(Message.id == message_id))
    await db.commit()
    return r.rowcount > 0


async def regenerate_last_ai_message(db, session_id: int, user_id: int) -> str:
    """
    Regenerates AI reply for the last USER message in the session.
    """

    # 1️⃣ Get last user message
    stmt = (
        select(Message)
        .where(
            Message.session_id == session_id,
            Message.role == "user",
            Message.user_id == user_id,
        )
        .order_by(desc(Message.created_at))
        .limit(1)
    )

    result = await db.execute(stmt)
    last_user_message = result.scalar_one_or_none()

    if not last_user_message:
        raise ValueError("No user message to regenerate")

    # 2️⃣ Delete last AI message (optional but recommended)
    stmt = (
        select(Message)
        .where(
            Message.session_id == session_id,
            Message.role == "assistant",
        )
        .order_by(desc(Message.created_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    last_ai_message = result.scalar_one_or_none()

    if last_ai_message:
        await db.delete(last_ai_message)

    # 3️⃣ Generate AI again
    ai_reply = generate_response(
        last_user_message.content,
        ""
    )

    # 4️⃣ Save new AI message
    new_ai_message = Message(
        session_id=session_id,
        role="assistant",
        content=ai_reply,
        user_id=user_id,
    )

    db.add(new_ai_message)
    await db.commit()

    return ai_reply

async def get_next_assistant_message(db: AsyncSession, user_message_id: int) -> Optional[dict]:
    """
    Get the FIRST assistant message that comes immediately after the given user message.
    REQUIRED for message-edit + regeneration.
    """
    # Get the user msg first
    r = await db.execute(select(Message).where(Message.id == user_message_id))
    user_msg = r.scalar_one_or_none()
    if not user_msg:
        return None

    # Find assistant reply after it
    r2 = await db.execute(
        select(Message)
        .where(
            Message.session_id == user_msg.session_id,
            Message.role == "assistant",
            Message.created_at > user_msg.created_at,
            Message.deleted == False
        )
        .order_by(Message.created_at.asc())
        .limit(1)
    )
    reply = r2.scalar_one_or_none()
    return reply.to_dict() if reply else None


async def can_edit_message(db: AsyncSession, message_id: int, session_id: int, user_id: int):
    """
    Checks if the message is allowed to be edited.
    Conditions:
    1. Message belongs to the session
    2. Message belongs to the user
    3. Message is the last USER message
    """
    
    # 1. Fetch the message
    result = await db.execute(
        select(Message).where(Message.id == message_id, Message.deleted == False)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        return False, "Message not found."

    # 2. Check ownership
    if msg.user_id != user_id:
        return False, "Cannot edit another user's message."

    # 3. Check session ownership
    if msg.session_id != session_id:
        return False, "Message does not belong to this session."

    # 4. Check if it's the LAST user message
    last_user_msg = await db.execute(
        select(Message)
        .where(
            Message.session_id == session_id,
            Message.role == "user",
            Message.deleted == False
        )
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    last_user_msg = last_user_msg.scalar_one_or_none()

    if not last_user_msg or last_user_msg.id != message_id:
        return False, "Only the latest user message can be edited."

    return True, "OK"


# =========================================================
# RISK/SIGNAL HELPERS
# =========================================================

async def get_recent_user_messages(
    db: AsyncSession,
    user_id: int,
    limit: int = 10,
    days: int = 30
) -> List[dict]:
    """Get recent user messages for analysis"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    r = await db.execute(
        select(Message)
        .where(
            Message.user_id == user_id,
            Message.role == "user",
            Message.deleted == False,
            Message.created_at >= cutoff
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    return [m.to_dict() for m in r.scalars().all()]


async def get_session_message_count(db: AsyncSession, session_id: int) -> int:
    """Count non-deleted messages in a session"""
    r = await db.execute(
        select(func.count(Message.id))
        .where(
            Message.session_id == session_id,
            Message.deleted == False
        )
    )
    return r.scalar() or 0


async def user_owns_session(db: AsyncSession, user_id: int, session_id: int) -> bool:
    """Check if user owns a session"""
    r = await db.execute(
        select(Session).where(Session.id == session_id, Session.user_id == user_id)
    )
    return bool(r.scalar_one_or_none())


async def get_all_messages_for_user(db: AsyncSession, user_id: int) -> List[dict]:
    """Get all messages for a user across all sessions"""
    r = await db.execute(
        select(Message)
        .where(
            Message.user_id == user_id,
            Message.deleted == False
        )
        .order_by(Message.created_at.asc())
    )
    return [m.to_dict() for m in r.scalars().all()]

def _get_dominant_emotion(emotions: list[str]) -> str:
    if not emotions:
        return "neutral"
    return max(set(emotions), key=emotions.count)

async def upsert_daily_emotion_summary(
    db: AsyncSession,
    user_id: int,
    target_date: date,
):
    """
    Create or update daily emotion summary for a user.
    Runs after each USER message.
    """

    try:
        # Fetch all NON-DELETED USER messages for the given date
        result = await db.execute(
            select(Message).where(
                Message.user_id == user_id,
                Message.role == "user",
                Message.deleted == False,
                func.date(Message.created_at) == target_date,
            )
        )

        messages = result.scalars().all()

        # 🚨 Skip days with no user messages
        if not messages:
            return None

        emotions = [m.emotion for m in messages if m.emotion]
        loneliness_scores = [
            m.loneliness_score
            for m in messages
            if m.loneliness_score is not None
        ]

        dominant_emotion = _get_dominant_emotion(emotions)
        avg_loneliness = (
            sum(loneliness_scores) / len(loneliness_scores)
            if loneliness_scores else None
        )

        # Check if summary exists
        existing = await db.execute(
            select(DailyEmotionSummary).where(
                DailyEmotionSummary.user_id == user_id,
                DailyEmotionSummary.date == target_date,
            )
        )
        summary = existing.scalar_one_or_none()

        if summary:
            summary.dominant_emotion = dominant_emotion
            summary.avg_loneliness = avg_loneliness
            summary.message_count = len(messages)
        else:
            summary = DailyEmotionSummary(
                user_id=user_id,
                date=target_date,
                dominant_emotion=dominant_emotion,
                avg_loneliness=avg_loneliness,
                message_count=len(messages),
            )
            db.add(summary)

        await db.commit()
        await db.refresh(summary)
        return summary

    except Exception:
        await db.rollback()
        raise

async def get_calendar_emotions(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
):
    """
    Returns daily emotion summaries for calendar month view
    """

    result = await db.execute(
        select(DailyEmotionSummary)
        .where(
            DailyEmotionSummary.user_id == user_id,
            DailyEmotionSummary.date >= start_date,
            DailyEmotionSummary.date <= end_date,
        )
        .order_by(DailyEmotionSummary.date.asc())
    )

    return [row.to_dict() for row in result.scalars().all()]

async def get_weekly_emotion_trend(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
):
    """
    Used for weekly emotional trend graphs
    """

    result = await db.execute(
        select(
            DailyEmotionSummary.date,
            DailyEmotionSummary.avg_loneliness,
            DailyEmotionSummary.message_count,
        )
        .where(
            DailyEmotionSummary.user_id == user_id,
            DailyEmotionSummary.date >= start_date,
            DailyEmotionSummary.date <= end_date,
        )
        .order_by(DailyEmotionSummary.date.asc())
    )

    return [
        {
            "date": row.date.isoformat(),
            "avg_loneliness": row.avg_loneliness,
            "message_count": row.message_count,
        }
        for row in result.all()
    ]

