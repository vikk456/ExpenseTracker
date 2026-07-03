from fastapi import APIRouter, Depends, UploadFile, File
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session
from database import get_db
from auth.utils import get_current_user
from expenses.models import Expense
from agent.ocr import extract_text_from_receipt
from agent.extractor import extract_expense_data
from agent.query_agent import create_query_agent
from schemas.models import ExpenseResponse
import base64
from datetime import datetime
from dateutil import parser as dateparser
from schemas.models import QueryRequest
import json

router = APIRouter()

@router.post("/upload", response_model=ExpenseResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image_bytes = await file.read()
    receipt_base64 = base64.b64encode(image_bytes).decode("utf-8")
    text = extract_text_from_receipt(image_bytes)
    expense_data = extract_expense_data(text)

    try:
        expense_date = dateparser.parse(expense_data["date"])
    except:
        expense_date = datetime.now()

    new_expense = Expense(
        user_id=user_id,
        vendor=expense_data["vendor"],
        date=expense_date,
        subtotal=expense_data["subtotal"],
        tax=expense_data["tax"],
        total=expense_data["total"],
        category=expense_data["category"],
        summary=expense_data["summary"],
        receipt=receipt_base64
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/profile", response_model=list[ExpenseResponse])
async def get_profile(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
    return expenses



@router.post("/query")
async def query_expenses(
    req: QueryRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = create_query_agent(db)
    result = agent.invoke({
        "messages": [HumanMessage(content=f"user_id: {user_id}\n\nQuestion: {req.query}")]
    })
    
    analysis = result["messages"][-1].content
    table_data = None
    
    for msg in result["messages"]:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            try:
                parsed = ast.literal_eval(msg.content)
                if isinstance(parsed, list) and len(parsed) > 0:
                    table_data = json.dumps(parsed)
                    break
            except:
                pass

    return {"response": analysis, "table_data": table_data}