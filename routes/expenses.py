from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Expense


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ADD EXPENSE
# =========================
@router.post("/add")
def add_expense(
    user_id: int,
    category: str,
    amount: float,
    description: str = "",
    date: str = "",
    db: Session = Depends(get_db)
):

    expense = Expense(
        user_id=user_id,
        category=category,
        amount=amount,
        description=description,
        date=date
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return {
        "status": "success",
        "message": "Expense added successfully",
        "expense": {
            "id": expense.id,
            "user_id": expense.user_id,
            "category": expense.category,
            "amount": expense.amount,
            "description": expense.description,
            "date": expense.date
        }
    }


# =========================
# GET USER EXPENSES
# =========================
@router.get("/user/{user_id}")
def get_expenses(
    user_id: int,
    db: Session = Depends(get_db)
):

    expenses = db.query(Expense).filter(
        Expense.user_id == user_id
    ).all()

    return {
        "status": "success",
        "count": len(expenses),
        "expenses": [
            {
                "id": expense.id,
                "category": expense.category,
                "amount": expense.amount,
                "description": expense.description,
                "date": expense.date
            }
            for expense in expenses
        ]
    }


# =========================
# UPDATE EXPENSE
# =========================
@router.put("/update/{expense_id}")
def update_expense(
    expense_id: int,
    user_id: int,
    category: str,
    amount: float,
    description: str = "",
    date: str = "",
    db: Session = Depends(get_db)
):

    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == user_id
    ).first()

    if not expense:
        return {
            "status": "error",
            "message": "Expense not found"
        }

    expense.category = category
    expense.amount = amount
    expense.description = description
    expense.date = date

    db.commit()
    db.refresh(expense)

    return {
        "status": "success",
        "message": "Expense updated successfully",
        "expense": {
            "id": expense.id,
            "category": expense.category,
            "amount": expense.amount,
            "description": expense.description,
            "date": expense.date
        }
    }


# =========================
# DELETE EXPENSE
# =========================
@router.delete("/delete/{expense_id}")
def delete_expense(
    expense_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):

    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == user_id
    ).first()

    if not expense:
        return {
            "status": "error",
            "message": "Expense not found"
        }

    db.delete(expense)
    db.commit()

    return {
        "status": "success",
        "message": "Expense deleted successfully"
    }