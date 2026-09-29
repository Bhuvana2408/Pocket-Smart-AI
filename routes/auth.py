from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Register
@router.post("/register")
def register(
    name: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    # Check existing user
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        return {
            "status": "error",
            "message": "Email already registered"
        }

    # Create new user
    new_user = User(
        name=name,
        email=email,
        password=password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }


# Login
@router.post("/login")
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return {
            "status": "error",
            "message": "User not found"
        }

    if user.password != password:
        return {
            "status": "error",
            "message": "Incorrect password"
        }

    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


# Logout
@router.get("/logout")
def logout():
    return {
        "status": "success",
        "message": "Logout successful"
    }


# Auth test
@router.get("/test")
def auth_test():
    return {
        "status": "success",
        "message": "Auth router is working!"
    }