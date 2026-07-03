from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str

class UserLogin(BaseModel):
    email: str
    password: str

class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    vendor: str
    date: datetime
    subtotal: float
    tax: float
    total: float
    category: str
    summary: str
    receipt: str
    created_at: datetime

    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    query: str
