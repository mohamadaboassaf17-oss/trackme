from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
import re


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    salary_type: Optional[str] = "monthly"
    salary_amount: Optional[float] = 0.0

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3 or len(v) > 50:
            raise ValueError('اسم المستخدم يجب أن يكون بين 3 و 50 حرفاً')
        if not re.match(r'^[a-zA-Z0-9_\u0600-\u06FF]+$', v):
            raise ValueError('اسم المستخدم يحتوي على رموز غير مسموح بها')
        if re.search(r'[<>&"\']', v):
            raise ValueError('اسم المستخدم يحتوي على رموز غير مسموح بها')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        if not any(c.isupper() for c in v):
            raise ValueError('يجب أن تحتوي على حرف كبير واحد على الأقل')
        if not any(c.isdigit() for c in v):
            raise ValueError('يجب أن تحتوي على رقم واحد على الأقل')
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    salary_type: str
    salary_amount: float
    work_days_per_week: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AttendanceCreate(BaseModel):
    date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    hours_worked: Optional[float] = 0.0
    status: Optional[str] = "present"


class AttendanceUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    hours_worked: Optional[float] = None
    status: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    hours_worked: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    date: date
    amount: float = Field(gt=0, description="يجب أن يكون أكبر من صفر")
    category: str = Field(min_length=1, max_length=50)
    note: Optional[str] = Field(default=None, max_length=500)

    @field_validator('note', 'category')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        if v is None:
            return v
        v = re.sub(r'<[^>]+>', '', v)
        return v.strip()


class ExpenseUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    note: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    date: date
    amount: float
    category: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpenseSummary(BaseModel):
    period_start: date
    period_end: date
    total_amount: float
    by_category: dict
    count: int


class ShiftDefaultsUpdate(BaseModel):
    default_start_time: Optional[str] = None  # Format: "HH:MM"
    default_end_time: Optional[str] = None  # Format: "HH:MM"


class ShiftDefaultsResponse(BaseModel):
    default_start_time: Optional[str] = None
    default_end_time: Optional[str] = None


class SalaryUpdate(BaseModel):
    salary_type: str
    salary_amount: float


class SalaryResponse(BaseModel):
    salary_type: str
    salary_amount: float
    period_start: date
    period_end: date
    expected_work_days: int
    actual_present_days: int
    absent_days: int
    holiday_days: int
    daily_rate: float
    earned_salary: float
    difference: float


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    due_date: date
    saved_amount: Optional[float] = 0.0


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    due_date: Optional[date] = None
    saved_amount: Optional[float] = None


class GoalResponse(BaseModel):
    id: int
    user_id: int
    name: str
    target_amount: float
    due_date: date
    saved_amount: float
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class WealthCreate(BaseModel):
    date: date
    source: str
    amount: float
    note: Optional[str] = None


class WealthUpdate(BaseModel):
    date: Optional[date] = None
    source: Optional[str] = None
    amount: Optional[float] = None
    note: Optional[str] = None


class WealthResponse(BaseModel):
    id: int
    user_id: int
    date: date
    source: str
    amount: float
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class WorkDaysUpdate(BaseModel):
    work_days_per_week: int = Field(..., ge=5, le=6, description="Number of work days per week (5 or 6)")


class WorkDaysResponse(BaseModel):
    work_days_per_week: int
