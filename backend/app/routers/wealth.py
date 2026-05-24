from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Wealth, User
from app.schemas import WealthCreate, WealthUpdate, WealthResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/wealth", tags=["wealth"])


@router.post("/", response_model=WealthResponse, status_code=status.HTTP_201_CREATED)
def create_wealth(
    data: WealthCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = Wealth(
        user_id=current_user.id,
        date=data.date,
        source=data.source,
        amount=data.amount,
        note=data.note,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[WealthResponse])
def list_wealth(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = (
        db.query(Wealth)
        .filter(Wealth.user_id == current_user.id)
        .order_by(Wealth.date.desc())
        .all()
    )
    return records


@router.get("/{wealth_id}", response_model=WealthResponse)
def get_wealth(
    wealth_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Wealth)
        .filter(Wealth.id == wealth_id, Wealth.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="السجل غير موجود"
        )
    return record


@router.put("/{wealth_id}", response_model=WealthResponse)
def update_wealth(
    wealth_id: int,
    data: WealthUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Wealth)
        .filter(Wealth.id == wealth_id, Wealth.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="السجل غير موجود"
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{wealth_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wealth(
    wealth_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(Wealth)
        .filter(Wealth.id == wealth_id, Wealth.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="السجل غير موجود"
        )
    db.delete(record)
    db.commit()
