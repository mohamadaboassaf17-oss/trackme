import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, Token, GoogleAuthRequest
from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    verify_google_token,
)
from app.utils.limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="الرجاء تسجيل الدخول"
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="بيانات الدخول غير صالحة"
        )
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="المستخدم غير موجود"
        )
    return user


def require_role(role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="غير مصرح لك بهذا الإجراء"
            )
        return current_user

    return role_checker


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("3/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="اسم المستخدم موجود مسبقاً"
        )
    hashed = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed,
        salary_type=user_data.salary_type,
        salary_amount=user_data.salary_amount,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/google", response_model=Token)
@limiter.limit("10/minute")
def google_login(request: Request, google_data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate user via Google ID token. Creates account if first time."""
    idinfo = verify_google_token(google_data.credential)
    if not idinfo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="فشل التحقق من حساب Google - الرجاء المحاولة مرة أخرى",
        )

    google_id = idinfo.get("sub")
    email = idinfo.get("email", "")
    name = idinfo.get("name", "")
    picture = idinfo.get("picture", "")

    if not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="بيانات حساب Google غير مكتملة",
        )

    user = db.query(User).filter(User.oauth_id == google_id).first()

    if not user and email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.oauth_provider = "google"
            user.oauth_id = google_id
            if picture and not user.avatar_url:
                user.avatar_url = picture
            db.commit()
            db.refresh(user)

    if not user:
        base_username = email.split("@")[0] if email else name.replace(" ", "_").lower()
        username = base_username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1

        random_password = get_password_hash(os.urandom(24).hex())

        new_user = User(
            username=username,
            email=email,
            password_hash=random_password,
            role="employee",
            oauth_provider="google",
            oauth_id=google_id,
            avatar_url=picture,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user

    token = create_access_token(
        {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
        }
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if not db_user or not verify_password(user_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="اسم المستخدم أو كلمة المرور غير صحيحة",
        )
    token = create_access_token(
        {
            "sub": str(db_user.id),
            "username": db_user.username,
            "role": db_user.role,
        }
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
