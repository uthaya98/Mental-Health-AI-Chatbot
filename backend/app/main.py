from fastapi import FastAPI
import logging

from app.api import users, chat, health, sessions, calendar
from app.db.database import engine
from app.db.models import Base
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("mental-health-ai")

app = FastAPI(
    title="Mental Health AI Backend",
    version="1.0.0",
    docs_url="/docs",              # Swagger UI at /docs
    redoc_url="/redoc",            # ReDoc at /redoc  
    openapi_url="/openapi.json"    # OpenAPI schema at /openapi.json
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include routers with /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")



@app.get("/")
def root():
    return {
        "service": "Mental Health AI Backend",
        "status": "running"
    }