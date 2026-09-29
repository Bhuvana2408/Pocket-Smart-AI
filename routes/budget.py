from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Budget


router = APIRouter(
    prefix="/budget",
    tags=["Budget"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ADD BUDGET
# =========================
@router.post("/add")
def add_budget(
    user_id: int,
    category: str,
    amount: float,
    db: Session = Depends(get_db)
):

    budget = Budget(
        user_id=user_id,
        category=category,
        amount=amount
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    return {
        "status": "success",
        "message": "Budget added successfully",
        "budget": {
            "id": budget.id,
            "user_id": budget.user_id,
            "category": budget.category,
            "amount": budget.amount
        }
    }


# =========================
# GET USER BUDGETS
# =========================
@router.get("/user/{user_id}")
def get_budgets(
    user_id: int,
    db: Session = Depends(get_db)
):

    budgets = db.query(Budget).filter(
        Budget.user_id == user_id
    ).all()

    return {
        "status": "success",
        "count": len(budgets),
        "budgets": [
            {
                "id": budget.id,
                "category": budget.category,
                "amount": budget.amount
            }
            for budget in budgets
        ]
    }


# =========================
# UPDATE BUDGET
# =========================
@router.put("/update/{budget_id}")
def update_budget(
    budget_id: int,
    user_id: int,
    category: str,
    amount: float,
    db: Session = Depends(get_db)
):

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()

    if not budget:
        return {
            "status": "error",
            "message": "Budget not found"
        }

    budget.category = category
    budget.amount = amount

    db.commit()
    db.refresh(budget)

    return {
        "status": "success",
        "message": "Budget updated successfully",
        "budget": {
            "id": budget.id,
            "category": budget.category,
            "amount": budget.amount
        }
    }


# =========================
# DELETE BUDGET
# =========================
@router.delete("/delete/{budget_id}")
def delete_budget(
    budget_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):

    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()

    if not budget:
        return {
            "status": "error",
            "message": "Budget not found"
        }

    db.delete(budget)
    db.commit()

    return {
        "status": "success",
        "message": "Budget deleted successfully"
    }