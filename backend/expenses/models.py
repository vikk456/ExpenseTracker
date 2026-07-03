from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from datetime import datetime
from database import Base

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vendor = Column(String)
    date = Column(DateTime)
    subtotal = Column(Float)
    tax = Column(Float)
    total = Column(Float)
    category = Column(String)
    summary = Column(String)
    receipt = Column(Text)
    created_at = Column(DateTime, default=datetime.now)