import os
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_google_token(token: str) -> dict | None:
    """Verify a Google-issued ID token and return the payload if valid."""
    # Strip quotes/whitespace that may be introduced by Render's env var paste
    raw_client_id = (os.getenv("GOOGLE_CLIENT_ID") or "").strip().strip('"').strip("'")
    if not raw_client_id:
        print("ERROR: GOOGLE_CLIENT_ID not set in environment")
        return None

    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            raw_client_id,
            clock_skew_in_seconds=60,
        )

        if idinfo.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            print(f"ERROR: Invalid issuer: {idinfo.get('iss')}")
            return None

        return idinfo

    except ValueError as e:
        prefix = raw_client_id[:10] if raw_client_id else "N/A"
        suffix = raw_client_id[-10:] if raw_client_id and len(raw_client_id) > 10 else "N/A"
        print(f"Google token verification failed: {e} | client_id: {prefix}...{suffix}")
        return None
    except Exception as e:
        print(f"Unexpected error during Google token verification: {e}")
        return None
