from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
from passlib.context import CryptContext
from datetime import datetime

from app.dependencies import get_db
from app.models.schemas import UserCreate, UserLogin
from app.db.crud import create_user, get_user_by_username
from app.core.auth import create_access_token   # ✅ SINGLE SOURCE

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------
# Password helpers
# ---------------------------------------------------------

def bcrypt_safe_hash(password: str) -> str:
    sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(sha256)

def verify_password(password: str, password_hash: str) -> bool:
    sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.verify(sha256, password_hash)

# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    req: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    password_hash = bcrypt_safe_hash(req.password)

    user = await create_user(
        db=db,
        username=req.username,
        email=req.email,
        password_hash=password_hash
    )

    token = create_access_token({
        "sub": str(user["id"])   # ✅ REQUIRED
    })

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "created_at": user["created_at"]
        }
    }

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@router.post("/login")
async def login_user(
    req: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_username(db, req.username)

    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({
        "sub": str(user["id"])   # ✅ MUST BE sub
    })

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "created_at": user["created_at"]
        }
    }
