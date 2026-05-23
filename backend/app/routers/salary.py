from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Attendance, User
from app.schemas import SalaryUpdate, SalaryResponse, UserResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["salary"])


def _count_weekdays(start: date, end: date) -> int:
    count = 0
    current = start
    while current <= end:
        if current.weekday() < 5:
            count += 1
        current += timedelta(days=1)
    return count


@router.put("/users/me", response_model=UserResponse)
def update_user_salary(
    data: SalaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.salary_type not in ("monthly", "weekly"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نوع الراتب يجب أن يكون شهري أو أسبوعي",
        )
    if data.salary_amount < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="مبلغ الراتب يجب أن يكون أكبر من أو يساوي صفر",
        )
    current_user.salary_type = data.salary_type
    current_user.salary_amount = data.salary_amount
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/salary", response_model=SalaryResponse)
def get_salary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    if current_user.salary_type == "weekly":
        period_start = today - timedelta(days=today.weekday())
    else:
        period_start = today.replace(day=1)

    period_end = today
    expected_work_days = _count_weekdays(period_start, period_end)

    records = (
        db.query(Attendance)
        .filter(
            Attendance.user_id == current_user.id,
            Attendance.date >= period_start,
            Attendance.date <= period_end,
        )
        .all()
    )

    actual_present_days = sum(1 for r in records if r.status == "present")
    absent_days = sum(1 for r in records if r.status == "absent")
    holiday_days = sum(1 for r in records if r.status == "holiday")

    if expected_work_days > 0:
        daily_rate = current_user.salary_amount / expected_work_days
    else:
        daily_rate = 0.0

    earned_salary = round(daily_rate * actual_present_days, 2)
    difference = round(current_user.salary_amount - earned_salary, 2)

    return SalaryResponse(
        salary_type=current_user.salary_type,
        salary_amount=current_user.salary_amount,
        period_start=period_start,
        period_end=period_end,
        expected_work_days=expected_work_days,
        actual_present_days=actual_present_days,
        absent_days=absent_days,
        holiday_days=holiday_days,
        daily_rate=round(daily_rate, 2),
        earned_salary=earned_salary,
        difference=difference,
    )
