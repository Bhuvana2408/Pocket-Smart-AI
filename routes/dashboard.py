from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models import Expense, Budget


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}")
def get_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):
    total_expenses = db.query(
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id
    ).scalar() or 0

    total_budget = db.query(
        func.sum(Budget.amount)
    ).filter(
        Budget.user_id == user_id
    ).scalar() or 0

    remaining = total_budget - total_expenses

    return {
        "status": "success",
        "dashboard": {
            "user_id": user_id,
            "total_budget": total_budget,
            "total_expenses": total_expenses,
            "remaining_budget": remaining
        }
    }