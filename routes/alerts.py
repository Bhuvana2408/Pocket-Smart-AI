from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models import Expense, Budget


router = APIRouter(
    prefix="/alerts",
    tags=["Budget Alerts"]
)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# GET BUDGET ALERTS
# ==========================================

@router.get("/{user_id}")
def get_budget_alerts(
    user_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------
    # Get user's budgets
    # --------------------------------------

    budgets = db.query(Budget).filter(
        Budget.user_id == user_id
    ).all()


    # --------------------------------------
    # Get user's expenses category-wise
    # --------------------------------------

    expense_rows = db.query(
        Expense.category,
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id
    ).group_by(
        Expense.category
    ).all()


    # Convert expenses into dictionary
    expense_by_category = {
        category: amount or 0
        for category, amount in expense_rows
    }


    # --------------------------------------
    # Combine budgets category-wise
    # --------------------------------------

    budget_by_category = {}

    for budget in budgets:

        if budget.category not in budget_by_category:
            budget_by_category[budget.category] = 0

        budget_by_category[budget.category] += budget.amount


    # --------------------------------------
    # Generate alerts
    # --------------------------------------

    alerts = []

    for category, budget_amount in budget_by_category.items():

        spent_amount = expense_by_category.get(
            category,
            0
        )

        # Avoid division by zero
        if budget_amount > 0:
            percentage = (
                spent_amount / budget_amount
            ) * 100
        else:
            percentage = 0


        # ==================================
        # BUDGET EXCEEDED
        # ==================================

        if percentage >= 100:

            alerts.append({
                "category": category,
                "budget": budget_amount,
                "spent": spent_amount,
                "percentage": round(percentage, 2),
                "severity": "danger",
                "message": (
                    f"🚨 {category} budget exceeded! "
                    f"You spent ₹{spent_amount:.2f} "
                    f"out of ₹{budget_amount:.2f}."
                )
            })


        # ==================================
        # 80% WARNING
        # ==================================

        elif percentage >= 80:

            alerts.append({
                "category": category,
                "budget": budget_amount,
                "spent": spent_amount,
                "percentage": round(percentage, 2),
                "severity": "warning",
                "message": (
                    f"⚠️ {category} spending reached "
                    f"{percentage:.2f}% of your budget."
                )
            })


    # --------------------------------------
    # Overall budget calculation
    # --------------------------------------

    total_budget = sum(
        budget_by_category.values()
    )

    total_expenses = sum(
        expense_by_category.values()
    )

    remaining_budget = (
        total_budget - total_expenses
    )


    # --------------------------------------
    # Overall alert
    # --------------------------------------

    overall_percentage = 0

    if total_budget > 0:

        overall_percentage = (
            total_expenses / total_budget
        ) * 100


    if overall_percentage >= 100:

        alerts.insert(0, {
            "category": "Overall Budget",
            "budget": total_budget,
            "spent": total_expenses,
            "percentage": round(
                overall_percentage,
                2
            ),
            "severity": "danger",
            "message": (
                "🚨 Your overall budget has been exceeded!"
            )
        })

    elif overall_percentage >= 80:

        alerts.insert(0, {
            "category": "Overall Budget",
            "budget": total_budget,
            "spent": total_expenses,
            "percentage": round(
                overall_percentage,
                2
            ),
            "severity": "warning",
            "message": (
                f"⚠️ Your overall budget is "
                f"{overall_percentage:.2f}% used."
            )
        })


    # --------------------------------------
    # Final response
    # --------------------------------------

    return {
        "status": "success",

        "user_id": user_id,

        "summary": {
            "total_budget": total_budget,
            "total_expenses": total_expenses,
            "remaining_budget": remaining_budget,
            "budget_used_percentage": round(
                overall_percentage,
                2
            )
        },

        "alert_count": len(alerts),

        "alerts": alerts
    }