from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from pydantic import BaseModel

load_dotenv()

class ExpenseData(BaseModel):
    vendor: str
    date: str
    subtotal: str
    tax: str
    total: str
    category: str
    summary: str

model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

model = model.with_structured_output(ExpenseData)

def extract_expense_data(text: str) -> dict:
    prompt = f"""Extract expense details from this receipt text.
Format date as DD-MM-YYYY. If any field is unknown, make a reasonable guess.
Return subtotal, tax, and total as plain numbers without currency symbols.

Receipt text:
{text}"""
    
    response = model.invoke(prompt)
    
    def clean_float(value: str) -> float:
        try:
            return float(str(value).replace(',', '').replace('$', '').replace('₹', '').replace('Rs', '').strip())
        except:
            return 0.0

    return {
        "vendor": response.vendor,
        "date": response.date,
        "subtotal": clean_float(response.subtotal),
        "tax": clean_float(response.tax),
        "total": clean_float(response.total),
        "category": response.category,
        "summary": response.summary
    }