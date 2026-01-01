from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.core.auth import get_current_user
from app.db.crud import (
    get_calendar_emotions,
    get_weekly_emotion_trend,
)
from app.models.schemas import CalendarDayResponse, WeeklyEmotionResponse

router = APIRouter(prefix="/calendar", tags=["calendar"])


# =========================================================
# 📅 GET /calendar/month
# =========================================================
@router.get("/month", response_model=list[CalendarDayResponse])
async def get_month_calendar(
    year: int = Query(..., example=2025),
    month: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Returns daily emotional summary for a full month.
    Used to populate calendar heatmap.
    """

    try:
        start_date = date(year, month, 1)

        # compute last day of month safely
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid year or month")

    data = await get_calendar_emotions(
        db=db,
        user_id=user["id"],
        start_date=start_date,
        end_date=end_date,
    )

    return data


# =========================================================
# 📊 GET /calendar/weekly-trend
# =========================================================
@router.get("/weekly-trend", response_model=list[WeeklyEmotionResponse])
async def get_weekly_trend(
    start_date: date = Query(..., example="2025-12-01"),
    end_date: date = Query(..., example="2025-12-07"),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Returns weekly emotional trend data.
    Used for line / bar chart.
    """

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

    return await get_weekly_emotion_trend(
        db=db,
        user_id=user["id"],
        start_date=start_date,
        end_date=end_date,
    )


# =========================================================
# 🧠 GET /calendar/daily-reflection
# =========================================================
@router.get("/daily-reflection")
async def get_daily_reflection(
    target_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Returns AI-generated reflection for a specific day.
    """

    records = await get_calendar_emotions(
        db=db,
        user_id=user["id"],
        start_date=target_date,
        end_date=target_date,
    )

    if not records:
        return {
            "date": target_date,
            "reflection": "No conversations recorded for this day."
        }

    day = records[0]

    # 🧠 Reflection logic (rule-based, safe, explainable)
    emotion = day["dominant_emotion"]
    loneliness = day["avg_loneliness"]
    count = day["message_count"]

    reflection = (
        f"On {target_date}, you shared {count} messages. "
        f"The dominant emotion detected was '{emotion}'. "
    )

    if loneliness is not None:
        if loneliness > 6:
            reflection += (
                "Your loneliness score was higher than usual. "
                "It may help to reach out to someone you trust."
            )
        elif loneliness < 3:
            reflection += (
                "You appeared emotionally stable and connected."
            )
        else:
            reflection += (
                "Your emotional state appeared balanced."
            )

    return {
        "date": target_date,
        "reflection": reflection,
        "emotion": emotion,
        "avg_loneliness": loneliness,
        "message_count": count,
    }
