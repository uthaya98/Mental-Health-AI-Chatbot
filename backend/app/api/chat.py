from datetime import datetime, date
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.core.auth import get_current_user
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatMessage,
    UpdateMessageRequest,
)
from app.db.crud import (
    create_message,
    get_messages_by_session,
    get_session,
    update_session_activity,
    get_next_assistant_message,
    update_message_in_session,
    soft_delete_message,
    get_sessions_by_user,
    get_all_messages_for_user,
    upsert_daily_emotion_summary,
    regenerate_last_ai_message
)
from app.services.emotion import detect_emotion, dominant_emotion
from app.services.loneliness import loneliness_score
from app.services.rag import retrieve_rag_docs, build_context_text
from app.services.llm import generate_response
from app.services.safety_check import safety_check
from app.services.drift import compute_emotional_drift

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger("mental-health-ai")


# =========================================================
# POST /chat → Send message
# =========================================================
@router.post("/", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    session = await get_session(db, req.session_id)
    if not session or session["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Session not found")

    # Emotion & loneliness
    emotion_scores = detect_emotion(req.message)
    emotion, _ = dominant_emotion(emotion_scores)
    loneliness = loneliness_score(req.message)["loneliness_score"]

    # Save USER message
    await create_message(
        db=db,
        session_id=req.session_id,
        user_id=user["id"],
        role="user",
        content=req.message,
        emotion=emotion,
        loneliness_score=loneliness,
    )

    await upsert_daily_emotion_summary(
        db=db,
        user_id=user["id"],
        target_date=date.today(),
    )

    # Safety check
    safety = safety_check([{
        "post": req.message,
        "date": datetime.utcnow(),
        "loneliness_score": loneliness,
        "suicidality_total": 0,
    }])

    print(f"safety is {safety}")

    # Crisis response
    if safety["risk_level"] == "high":
        crisis_text = (
            "I'm really glad you reached out. "
            "If you're in immediate danger, please contact emergency services "
            "or a suicide prevention hotline."
        )

        await create_message(
            db=db,
            session_id=req.session_id,
            user_id=user["id"],
            role="assistant",
            content=crisis_text,
            emotion=None,
            loneliness_score=None,
        )

        return ChatResponse(
            reply=crisis_text,
            emotion=emotion,
            loneliness_score=loneliness,
            is_crisis_response=True,
            risk_level="high",
            risk_score=safety["risk_score"],
        )

    # Normal AI response
    context = build_context_text(retrieve_rag_docs(req.message))
    ai_reply = generate_response(req.message, context)

    await create_message(
        db=db,
        session_id=req.session_id,
        user_id=user["id"],
        role="assistant",
        content=ai_reply,
        emotion=None,
        loneliness_score=None,
    )

    await update_session_activity(db, req.session_id)

    return ChatResponse(
        reply=ai_reply,
        emotion=emotion,
        loneliness_score=loneliness,
        risk_level=safety["risk_level"],
        risk_score=safety["risk_score"],
    )


# =========================================================
# GET /chat/history/{session_id}
# =========================================================
@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    session = await get_session(db, session_id)
    if not session or session["user_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Session not found")

    raw_messages = await get_messages_by_session(db, session_id)

    messages = [
        ChatMessage(
            id=m["id"],
            session_id=m["session_id"],
            user_id=m["user_id"],
            role=m["role"],
            content=m["content"],   # ✅ FIXED
            emotion=m["emotion"],
            loneliness_score=m["loneliness_score"],
            created_at=m["created_at"],
            updated_at=m.get("updated_at"),
        )
        for m in raw_messages
    ]

    drift = compute_emotional_drift(raw_messages)

    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages,
        drift_score=drift.get("drift_score"),
        status=drift.get("status"),
    )


# =========================================================
# PUT /chat/{session_id}/message/{message_id}
# Edit latest user message + regenerate
# =========================================================
@router.put("/{session_id}/message/{message_id}", response_model=ChatResponse)
async def edit_and_regenerate(
    session_id: int,
    message_id: int,
    req: UpdateMessageRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    session = await get_session(db, session_id)
    if not session or session["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    updated = await update_message_in_session(
        db=db,
        session_id=session_id,
        message_id=message_id,
        user_id=user["id"],
        new_content=req.content,
    )

    if not updated:
        raise HTTPException(
            status_code=403,
            detail="Only the latest user message can be edited",
        )

    # Remove old assistant reply
    assistant = await get_next_assistant_message(db, message_id)
    if assistant:
        await soft_delete_message(db, assistant["id"])

    # Generate new response
    context = build_context_text(retrieve_rag_docs(req.content))
    ai_reply = generate_response(req.content, context)

    await create_message(
        db=db,
        session_id=session_id,
        user_id=user["id"],
        role="assistant",
        content=ai_reply,
        emotion=None,
        loneliness_score=None,
    )

    return ChatResponse(reply=ai_reply)

@router.post("/{session_id}/regenerate", response_model=ChatResponse)
async def regenerate_last_message(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Regenerate AI response for the LAST user message only.
    """
    ai_reply = await regenerate_last_ai_message(
        db=db,
        session_id=session_id,
        user_id=user["id"],
    )

    return ChatResponse(reply=ai_reply)

# =========================================================
# GET /chat/user/me/sessions
# =========================================================
@router.get("/user/me/sessions")
async def get_my_sessions(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    sessions = await get_sessions_by_user(db, user["id"])
    return {"sessions": sessions}


# =========================================================
# GET /chat/user/me/history
# =========================================================
@router.get("/user/me/history")
async def get_my_full_history(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    messages = await get_all_messages_for_user(db, user["id"])
    return {
        "user_id": user["id"],
        "total_messages": len(messages),
        "messages": messages,
    }
