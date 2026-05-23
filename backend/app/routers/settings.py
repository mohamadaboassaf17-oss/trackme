from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import ShiftDefaultsUpdate, ShiftDefaultsResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.put("/shift-defaults", response_model=ShiftDefaultsResponse)
def update_shift_defaults(
    data: ShiftDefaultsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import time

    if data.default_start_time:
        h, m = map(int, data.default_start_time.split(":"))
        current_user.default_start_time = time(h, m)
    if data.default_end_time:
        h, m = map(int, data.default_end_time.split(":"))
        current_user.default_end_time = time(h, m)
    db.commit()
    db.refresh(current_user)
    return ShiftDefaultsResponse(
        default_start_time=current_user.default_start_time.strftime("%H:%M")
        if current_user.default_start_time
        else None,
        default_end_time=current_user.default_end_time.strftime("%H:%M")
        if current_user.default_end_time
        else None,
    )


@router.get("/shift-defaults", response_model=ShiftDefaultsResponse)
def get_shift_defaults(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ShiftDefaultsResponse(
        default_start_time=current_user.default_start_time.strftime("%H:%M")
        if current_user.default_start_time
        else None,
        default_end_time=current_user.default_end_time.strftime("%H:%M")
        if current_user.default_end_time
        else None,
    )
