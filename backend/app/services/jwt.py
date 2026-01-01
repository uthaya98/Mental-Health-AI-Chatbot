import jwt
from datetime import datetime, timedelta
from app.config import settings

JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = 60 * 24

def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "iat": datetime.now(),
        "exp": datetime.now() + timedelta(minutes=JWT_EXPIRES_MINUTES)
    }

    token = jwt.encode(
        payload,
        settings.OPENAI_API_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token