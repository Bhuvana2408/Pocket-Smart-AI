from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from google import genai
from dotenv import load_dotenv

from pathlib import Path
import os
import time

from app.database import SessionLocal
from app.models import Expense, Budget, Recommendation


# ==================================================
# ENVIRONMENT
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


# ==================================================
# ROUTER
# ==================================================

router = APIRouter(
    prefix="/recommendations",
    tags=["AI Recommendations"]
)


# ==================================================
# DATABASE
# ==================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==================================================
# AI RECOMMENDATION HISTORY
# ==================================================

@router.get("/history/{user_id}")
def get_recommendation_history(
    user_id: int,
    db: Session = Depends(get_db)
):

    recommendations = db.query(
        Recommendation
    ).filter(
        Recommendation.user_id == user_id
    ).order_by(
        Recommendation.id.desc()
    ).all()

    return {
        "status": "success",
        "count": len(recommendations),

        "recommendations": [
            {
                "id": recommendation.id,
                "title": recommendation.title,
                "message": recommendation.message
            }

            for recommendation in recommendations
        ]
    }


# ==================================================
# GENERATE AI RECOMMENDATION
# ==================================================

@router.get("/{user_id}")
def get_recommendations(
    user_id: int,
    db: Session = Depends(get_db)
):

    # ------------------------------------------------
    # TOTAL EXPENSES
    # ------------------------------------------------

    total_expenses = db.query(
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == user_id
    ).scalar() or 0


    # ------------------------------------------------
    # TOTAL BUDGET
    # ------------------------------------------------

    total_budget = db.query(
        func.sum(Budget.amount)
    ).filter(
        Budget.user_id == user_id
    ).scalar() or 0


    # ------------------------------------------------
    # REMAINING BUDGET
    # ------------------------------------------------

    remaining = total_budget - total_expenses


    # ------------------------------------------------
    # EXPENSE DETAILS
    # ------------------------------------------------

    expenses = db.query(
        Expense
    ).filter(
        Expense.user_id == user_id
    ).all()


    expense_details = []

    for expense in expenses:

        expense_details.append(
            f"Category: {expense.category}, "
            f"Amount: ₹{expense.amount}, "
            f"Description: {expense.description or 'None'}, "
            f"Date: {expense.date or 'None'}"
        )


    expense_text = "\n".join(expense_details)


    # ------------------------------------------------
    # API KEY
    # ------------------------------------------------

    api_key = os.getenv("GEMINI_API_KEY")


    if not api_key:

        return {
            "status": "error",
            "message": "GEMINI_API_KEY is not loaded",
            "env_file": str(ENV_FILE),
            "env_file_exists": ENV_FILE.exists()
        }


    # =================================================
    # GEMINI
    # =================================================

    try:

        client = genai.Client(
            api_key=api_key
        )


        # ------------------------------------------------
        # PROMPT
        # ------------------------------------------------

        prompt = f"""
You are a personal finance assistant for Pocket Smart AI.

User ID:
{user_id}

Total Budget:
₹{total_budget}

Total Expenses:
₹{total_expenses}

Remaining Budget:
₹{remaining}

Expense Details:
{expense_text}

Analyze the user's spending.

Provide:

1. Spending Summary
2. Main Spending Category
3. Unnecessary Spending Areas
4. Saving Suggestions
5. Budget Management Advice

Use simple English.

Give practical and easy-to-understand suggestions.

Do not give risky investment recommendations.
"""


        # ------------------------------------------------
        # GENERATE RESPONSE
        # ------------------------------------------------

        response = None


        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )

                break


            except Exception as e:

                error_text = str(e)


                # ----------------------------------------
                # TEMPORARY 503 ERROR
                # ----------------------------------------

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                ):

                    if attempt < 2:

                        time.sleep(3)

                        continue

                    return {
                        "status": "error",
                        "message": "Gemini AI is temporarily busy. Please try again later.",
                        "details": error_text
                    }


                # ----------------------------------------
                # QUOTA ERROR
                # ----------------------------------------

                if (
                    "429" in error_text
                    or "quota" in error_text.lower()
                    or "RESOURCE_EXHAUSTED" in error_text
                ):

                    demo_recommendation = f"""
Spending Summary:

Your total budget is ₹{total_budget} and your total expenses are ₹{total_expenses}.

Remaining Budget:

You currently have ₹{remaining} remaining.

Saving Suggestions:

1. Track your daily expenses regularly.
2. Reduce unnecessary spending.
3. Set category-wise spending limits.
4. Review your expenses every week.
5. Try to keep some amount as savings.

Budget Management Advice:

Keep your expenses within your planned budget and monitor high-spending categories.
"""


                    # Save demo recommendation

                    recommendation = Recommendation(
                        user_id=user_id,
                        title="AI Spending Recommendation (Demo)",
                        message=demo_recommendation
                    )


                    db.add(recommendation)

                    db.commit()

                    db.refresh(recommendation)


                    return {
                        "status": "success",
                        "mode": "demo",
                        "recommendation_id": recommendation.id,
                        "total_budget": total_budget,
                        "total_expenses": total_expenses,
                        "remaining_budget": remaining,
                        "ai_recommendation": demo_recommendation
                    }


                # ----------------------------------------
                # OTHER GEMINI ERROR
                # ----------------------------------------

                return {
                    "status": "error",
                    "message": "Gemini AI error",
                    "details": error_text
                }


        # =================================================
        # NO RESPONSE
        # =================================================

        if response is None:

            return {
                "status": "error",
                "message": "No response received from Gemini AI"
            }


        # =================================================
        # AI TEXT
        # =================================================

        ai_recommendation = response.text


        # =================================================
        # SAVE REAL AI RECOMMENDATION
        # =================================================

        recommendation = Recommendation(
            user_id=user_id,
            title="AI Spending Recommendation",
            message=ai_recommendation
        )


        db.add(recommendation)

        db.commit()

        db.refresh(recommendation)


        # =================================================
        # SUCCESS RESPONSE
        # =================================================

        return {
            "status": "success",
            "mode": "gemini",
            "user_id": user_id,
            "recommendation_id": recommendation.id,
            "total_budget": total_budget,
            "total_expenses": total_expenses,
            "remaining_budget": remaining,
            "expense_details": expense_details,
            "ai_recommendation": ai_recommendation
        }


    # =================================================
    # GENERAL ERROR
    # =================================================

    except Exception as e:

        return {
            "status": "error",
            "message": "Gemini AI error",
            "details": str(e)
        }