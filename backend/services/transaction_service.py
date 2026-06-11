from datetime import date
from typing import Any

from core.database import get_supabase


class TransactionService:
    async def create_transaction(
        self,
        business_id: str,
        type: str,
        amount: float,
        description: str = "",
        category: str | None = None,
        customer_name: str | None = None,
        vendor_name: str | None = None,
        payment_method: str = "cash",
        transaction_date: date | None = None,
        source: str = "whatsapp",
    ) -> dict[str, Any]:
        db = get_supabase()
        payload = {
            "business_id": business_id,
            "type": type,
            "amount": amount,
            "description": description,
            "category": category,
            "customer_name": customer_name,
            "vendor_name": vendor_name,
            "payment_method": payment_method,
            "transaction_date": (transaction_date or date.today()).isoformat(),
            "source": source,
        }
        result = db.table("transactions").insert(payload).execute()
        return result.data[0]

    async def get_monthly_total(
        self, business_id: str, tx_type: str, year: int | None = None, month: int | None = None
    ) -> float:
        today = date.today()
        year = year or today.year
        month = month or today.month
        start = date(year, month, 1).isoformat()
        if month == 12:
            end = date(year + 1, 1, 1).isoformat()
        else:
            end = date(year, month + 1, 1).isoformat()

        db = get_supabase()
        rows = (
            db.table("transactions")
            .select("amount")
            .eq("business_id", business_id)
            .eq("type", tx_type)
            .gte("transaction_date", start)
            .lt("transaction_date", end)
            .execute()
        )
        return float(sum(float(r["amount"]) for r in rows.data))

    async def list_transactions(
        self,
        business_id: str,
        tx_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        db = get_supabase()
        query = (
            db.table("transactions")
            .select("*")
            .eq("business_id", business_id)
            .order("transaction_date", desc=True)
            .limit(limit)
        )
        if tx_type:
            query = query.eq("type", tx_type)
        return query.execute().data

    async def monthly_summary(
        self, business_id: str, year: int, month: int
    ) -> dict[str, float]:
        sales = await self.get_monthly_total(business_id, "sale", year, month)
        expenses = await self.get_monthly_total(business_id, "expense", year, month)
        return {
            "revenue": sales,
            "expenses": expenses,
            "profit": sales - expenses,
        }
