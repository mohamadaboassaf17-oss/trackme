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


def verify_google_token(id_token: str) -> dict | None:
    """Verify a Google-issued ID token and return the payload if valid."""
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        if not client_id:
            print("ERROR: GOOGLE_CLIENT_ID not set in environment")
            return None

        idinfo = id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            client_id,
            clock_skew_in_seconds=60,
        )

        if idinfo.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            print(f"ERROR: Invalid issuer: {idinfo.get('iss')}")
            return None

        return idinfo

    except ValueError as e:
        print(f"Google token verification failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during Google token verification: {e}")
        return None
