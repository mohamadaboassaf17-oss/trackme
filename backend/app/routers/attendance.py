from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Attendance, User
from app.schemas import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.post(
    "/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED
)
def create_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = Attendance(
        user_id=current_user.id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        hours_worked=data.hours_worked,
        status=data.status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[AttendanceResponse])
def list_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = (
        db.query(Attendance)
        .filter(Attendance.user_id == current_user.id)
        .order_by(Attendance.date.desc())
        .all()
    )
    return records


@router.get("/{record_id}", response_model=AttendanceResponse)
def get_attendance(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Attendance)
        .filter(Attendance.id == record_id, Attendance.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="السجل غير موجود"
        )
    return record


@router.put("/{record_id}", response_model=AttendanceResponse)
def update_attendance(
    record_id: int,
    data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Attendance)
        .filter(Attendance.id == record_id, Attendance.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="السجل غير موجود"
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    # Auto-calculate hours_worked when both start_time and end_time are present
    if record.start_time and record.end_time:
        from datetime import datetime, time, timedelta
        start_dt = datetime.combine(record.date, record.start_time)
        end_dt = datetime.combine(record.date, record.end_time)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        diff = (end_dt - start_dt).total_seconds() / 3600
        record.hours_worked = round(diff, 1)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Attendance)
        .filter(Attendance.id == record_id, Attendance.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="السجل غير موجود"
        )
    db.delete(record)
    db.commit()
