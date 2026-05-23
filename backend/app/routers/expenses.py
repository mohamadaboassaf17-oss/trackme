from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Expense, User
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseSummary
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/expenses", tags=["expenses"])

DEFAULT_CATEGORIES = ["طعام", "إيجار", "مواصلات", "ترفيه", "صحة", "أخرى"]


def _get_period_range(period: str):
    today = date.today()
    if period == "weekly":
        start = today - timedelta(days=today.weekday())
        end = today
    else:
        start = today.replace(day=1)
        end = today
    return start, end


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = Expense(
        user_id=current_user.id,
        date=data.date,
        amount=data.amount,
        category=data.category,
        note=data.note,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[ExpenseResponse])
def list_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = (
        db.query(Expense)
        .filter(Expense.user_id == current_user.id)
        .order_by(Expense.date.desc())
        .all()
    )
    return records


@router.get("/summary", response_model=ExpenseSummary)
def get_expense_summary(
    period: str = Query("monthly", regex="^(weekly|monthly)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start, end = _get_period_range(period)

    records = (
        db.query(Expense)
        .filter(
            Expense.user_id == current_user.id,
            Expense.date >= start,
            Expense.date <= end,
        )
        .all()
    )

    total_amount = sum(r.amount for r in records)
    by_category = {}
    for r in records:
        by_category[r.category] = by_category.get(r.category, 0) + r.amount

    return ExpenseSummary(
        period_start=start,
        period_end=end,
        total_amount=round(total_amount, 2),
        by_category=by_category,
        count=len(records),
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="المصروف غير موجود"
        )
    return record


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="المصروف غير موجود"
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="المصروف غير موجود"
        )
    db.delete(record)
    db.commit()
