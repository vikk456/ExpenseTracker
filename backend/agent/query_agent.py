from sqlalchemy.orm import Session
from sqlalchemy import func
from expenses.models import Expense
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os

load_dotenv()

class QueryState(TypedDict):
    messages: Annotated[list, add_messages]

def create_query_agent(db: Session):

    @tool
    def get_all_expenses(user_id: int) -> str:
        """Get all expenses for a user including vendor, total, category and date."""
        expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
        return str([{
            "vendor": e.vendor,
            "total": e.total,
            "category": e.category,
            "date": str(e.date)
        } for e in expenses])

    @tool
    def get_expenses_by_category(user_id: int, category: str) -> str:
        """Get expenses filtered by category for a user."""
        expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.category == category
        ).all()
        return str([{
            "vendor": e.vendor,
            "total": e.total,
            "date": str(e.date)
        } for e in expenses])

    @tool
    def get_expenses_by_date_range(user_id: int, start_date: str, end_date: str) -> str:
        """Get expenses within a date range for a user. Dates should be in YYYY-MM-DD format."""
        expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).all()
        return str([{
            "vendor": e.vendor,
            "total": e.total,
            "category": e.category,
            "date": str(e.date)
        } for e in expenses])

    @tool
    def get_total_spending(user_id: int) -> str:
        """Get the total amount spent by a user across all expenses."""
        total = db.query(func.sum(Expense.total)).filter(
            Expense.user_id == user_id
        ).scalar()
        return f"Total spending: {total or 0}"

    @tool
    def get_spending_by_category(user_id: int) -> str:
        """Get total spending broken down by category for a user."""
        results = db.query(
            Expense.category,
            func.sum(Expense.total)
        ).filter(
            Expense.user_id == user_id
        ).group_by(Expense.category).all()
        return str([{"category": r[0], "total": r[1]} for r in results])

    tools = [
        get_all_expenses,
        get_expenses_by_category,
        get_expenses_by_date_range,
        get_total_spending,
        get_spending_by_category
    ]

    model = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    ).bind_tools(tools)

    def agent_node(state: QueryState):
        system_message = SystemMessage(content="""You are a helpful personal expense assistant.
Answer questions about the user's spending using the available tools.
Always use the user_id provided at the start of the conversation.
Be concise and clear in your responses.""")
        messages = [system_message] + state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(QueryState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()