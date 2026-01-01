from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db
from app.models.schemas import (
    SessionCreateRequest,
    SessionResponse
)
from app.db.crud import (
    create_session,
    get_sessions_by_user,
    get_session,
    delete_session
)
from app.core.auth import get_current_user  # 🔐 IMPORTANT

router = APIRouter(prefix="/sessions", tags=["sessions"])


# =========================================================
# POST /sessions
# =========================================================
@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_session(
    req: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)   # ✅ user from JWT
):
    """
    Create a new conversation session for the logged-in user.
    """
    session = await create_session(
        db=db,
        user_id=user["id"],   # ✅ NEVER from request body
        title=req.title or "Mental Health Check-in"
    )

    # ✅ CRUD already returns correct structure
    return SessionResponse(
        id=session["id"],        # 🔥 FIX HERE
        user_id=session["user_id"],
        title=session["title"],
        created_at=session["created_at"],
        updated_at=session.get("updated_at"),
    )


# =========================================================
# GET /sessions/user/me
# =========================================================
@router.get("/user/me", response_model=List[SessionResponse])
async def list_my_sessions(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Retrieve all sessions belonging to the logged-in user.
    """
    print(f"User ID : {user['id']}")
    return await get_sessions_by_user(db, user["id"])


# =========================================================
# GET /sessions/{session_id}
# =========================================================
@router.get("/{session_id}", response_model=SessionResponse)
async def get_session_details(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get a single session by ID (ownership enforced).
    """
    session = await get_session(db, session_id)

    if not session or session["user_id"] != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return session


# =========================================================
# DELETE /sessions/{session_id}
# =========================================================
@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Delete a session and all its messages.
    """
    session = await get_session(db, session_id)

    if not session or session["user_id"] != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    await delete_session(db, session_id)
    return None
