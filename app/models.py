from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(String(50), nullable=True)


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)