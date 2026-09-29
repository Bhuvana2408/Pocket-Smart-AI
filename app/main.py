from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine
from app import models

from routes.auth import router as auth_router
from routes.expenses import router as expense_router
from routes.budget import router as budget_router
from routes.dashboard import router as dashboard_router
from routes.recommendations import router as recommendation_router
from routes.alerts import router as alerts_router

# ==========================================
# CREATE DATABASE TABLES
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# CREATE TEMPLATES
# ==========================================

templates = Jinja2Templates(
    directory="templates"
)


# ==========================================
# CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Pocket Smart AI",
    description="Smart Budget and AI Assistant",
    version="1.0.0"
)


# ==========================================
# ROUTERS
# ==========================================

app.include_router(auth_router)

app.include_router(expense_router)

app.include_router(budget_router)

app.include_router(dashboard_router)

app.include_router(recommendation_router)

app.include_router(alerts_router)

# ==========================================
# DASHBOARD WEB PAGE
# ==========================================

@app.get("/dashboard-page")
def dashboard_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request
        }
    )

@app.get("/expenses-page")
def expenses_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="expenses.html",
        context={
            "request": request
        }
    )

@app.get("/budget-page")
def budget_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="budget.html",
        context={
            "request": request
        }
    )

@app.get("/reports-page")
def reports_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "request": request
        }
    )

@app.get("/history-page")
def history_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "request": request
        }
    )

@app.get("/ai-page")
def ai_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="ai.html",
        context={
            "request": request
        }
    )

@app.get("/ai-history-page")
def ai_history_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="ai-history.html",
        context={"request": request}
    )

@app.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request
        }
    )

@app.get("/register-page")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request
        }
    )

    
# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Welcome to Pocket Smart AI",
        "status": "Application is running successfully"
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "success",
        "message": "Pocket Smart AI is working!"
    }


# ==========================================
# API TEST
# ==========================================

@app.get("/api/test")
def test_api():

    return {
        "project": "Pocket Smart AI",
        "api": "working",
        "status": "success"
    }