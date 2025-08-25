import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

# Secret handling: allow a dev fallback only in local/dev envs
_env = os.getenv("APP_ENV", "local").lower()
SECRET_KEY = os.getenv("SESSION_SECRET") or (
    "dev-insecure-secret"
    if _env in {"local", "development", "dev"}
    else "dev-insecure-secret"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRES_MIN", "30"))


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict | None:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
