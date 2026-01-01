from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.dependencies import get_db

router = APIRouter(prefix="/health", tags=["health"])

# =========================================================
# Liveness probe
# =========================================================
@router.get("/live")
def liveness():
    """
    Liveness probe.
    Used by Kubernetes / container runtime
    to check if the app is running.
    """
    return {"status": "alive"}


# =========================================================
# Readiness probe
# =========================================================
@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe.
    Confirms SQLite DB is reachable and usable.
    """
    try:
        # Minimal DB operation
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "sqlite",
            "error": str(e)
        }

    return {
        "status": "healthy",
        "database": "sqlite",
        "db": db_status
    }
