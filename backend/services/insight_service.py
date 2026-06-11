from datetime import date, timedelta
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from core.config import settings
from core.database import get_supabase
from services.transaction_service import TransactionService
from services.udhaar_service import UdhaarService


class InsightService:
    def __init__(self) -> None:
        self.tx = TransactionService()
        self.udhaar = UdhaarService()

    async def weekly_insights(self, business_id: str, business_name: str) -> str:
        end = date.today()
        start = end - timedelta(days=7)
        db = get_supabase()
        rows = (
            db.table("transactions")
            .select("*")
            .eq("business_id", business_id)
            .gte("transaction_date", start.isoformat())
            .lte("transaction_date", end.isoformat())
            .execute()
            .data
        )

        sales = sum(float(r["amount"]) for r in rows if r["type"] == "sale")
        expenses = sum(float(r["amount"]) for r in rows if r["type"] == "expense")
        udhaar_out = await self.udhaar.outstanding_total(business_id)

        stats_text = (
            f"Business: {business_name}\n"
            f"Last 7 days sales: Rs. {sales:,.0f}\n"
            f"Last 7 days expenses: Rs. {expenses:,.0f}\n"
            f"Net: Rs. {sales - expenses:,.0f}\n"
            f"Outstanding udhaar: Rs. {udhaar_out:,.0f}\n"
            f"Transaction count: {len(rows)}"
        )

        if not settings.GROQ_API_KEY:
            return (
                f"📈 *Weekly Insights — {business_name}*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"💰 Sales (7d): Rs. {sales:,.0f}\n"
                f"💸 Expenses (7d): Rs. {expenses:,.0f}\n"
                f"📊 Net: Rs. {sales - expenses:,.0f}\n"
                f"⚠️ Udhaar outstanding: Rs. {udhaar_out:,.0f}"
            )

        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.3,
            max_tokens=400,
        )
        prompt = ChatPromptTemplate.from_template(
            """You are a Pakistani SME business advisor. Given weekly stats, write 3 short bullet insights and 1 actionable tip in Roman Urdu/English mix. Keep under 600 chars.

Stats:
{stats}

Format:
📈 *Weekly Business Insights*
━━━━━━━━━━━━━━━━━━━
• insight 1
• insight 2
• insight 3
━━━━━━━━━━━━━━━━━━━
💡 Tip: ..."""
        )
        chain = prompt | llm | StrOutputParser()
        return await chain.ainvoke({"stats": stats_text})
