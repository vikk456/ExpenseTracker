# ExpenseTracker — AI-Powered Expense Tracker

Upload receipts, let AI extract the details, and ask your spending anything — all in one beautifully simple dashboard.

🌐 **Live:** [expensetracker-gautam.vercel.app](https://expensetracker-gautam.vercel.app)

## Architecture
Receipt Image → OCR (Tesseract) → LLM Structured Output → SQLite/PostgreSQL
Natural Language Query → LangGraph ReAct Agent → DB Tools → Response

## Tech Stack
- **Backend**: FastAPI, LangGraph, LangChain, Groq (Llama 3.3)
- **Auth**: JWT tokens, bcrypt password hashing
- **OCR**: Tesseract via pytesseract
- **Database**: SQLAlchemy + SQLite (local) / PostgreSQL (production)
- **Frontend**: Vanilla JS, HTML, CSS (deployed on Vercel)
- **Backend Hosting**: Render (Docker)

## Features
- JWT-based user authentication (signup/login)
- Receipt OCR — extract text from any receipt image
- LLM structured output — automatically parse vendor, date, total, category, summary
- Natural language spending queries via LangGraph ReAct agent
- Profile page with spending analytics and receipt history

## Setup
```bash
cd backend
pip install -r requirements.txt
# Add GROQ_API_KEY and SECRET_KEY to backend/.env
uvicorn main:app --reload
```

## Limitations
- Groq free tier: 100k tokens/day
- OCR quality depends on receipt image clarity
- Free tier Render instance spins down after inactivity

## Author
Gautam — B.Tech CSE, IIIT Sri City