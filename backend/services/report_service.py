import uuid
from datetime import date
from typing import Any

from core.config import settings
from core.database import get_supabase
from generators.excel_report import generate_monthly_excel
from services.transaction_service import TransactionService
from services.udhaar_service import UdhaarService


class ReportService:
    def __init__(self) -> None:
        self.tx = TransactionService()
        self.udhaar = UdhaarService()

    async def build_monthly_data(
        self, business_id: str, year: int, month: int
    ) -> dict[str, list[dict[str, Any]]]:
        start = date(year, month, 1).isoformat()
        if month == 12:
            end = date(year + 1, 1, 1).isoformat()
        else:
            end = date(year, month + 1, 1).isoformat()

        db = get_supabase()
        txs = (
            db.table("transactions")
            .select("*")
            .eq("business_id", business_id)
            .gte("transaction_date", start)
            .lt("transaction_date", end)
            .execute()
            .data
        )
        sales = [t for t in txs if t["type"] == "sale"]
        expenses = [t for t in txs if t["type"] == "expense"]
        udhaar_given = await self.udhaar.list_by_business(business_id, "customer")
        udhaar_received = await self.udhaar.list_by_business(business_id, "supplier")
        invoices = (
            db.table("invoices")
            .select("*")
            .eq("business_id", business_id)
            .gte("invoice_date", start)
            .lt("invoice_date", end)
            .execute()
            .data
        )
        return {
            "sales": sales,
            "expenses": expenses,
            "udhaar_given": udhaar_given,
            "udhaar_received": udhaar_received,
            "invoices": invoices,
        }

    async def generate_excel_bytes(
        self, business_id: str, business_name: str, year: int, month: int
    ) -> bytes:
        data = await self.build_monthly_data(business_id, year, month)
        month_name = date(year, month, 1).strftime("%B")
        return generate_monthly_excel(data, business_name, month_name, year)

    async def upload_excel(
        self, business_id: str, filename: str, content: bytes
    ) -> str | None:
        db = get_supabase()
        path = f"{business_id}/reports/{filename}"
        bucket = settings.SUPABASE_STORAGE_BUCKET
        try:
            db.storage.from_(bucket).upload(
                path,
                content,
                {
                    "content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "upsert": "true",
                },
            )
            signed = db.storage.from_(bucket).create_signed_url(path, 60 * 60 * 24 * 7)
            return signed.get("signedURL") or signed.get("signedUrl")
        except Exception:
            return None

    async def text_monthly_report(
        self, business_id: str, business_name: str, year: int, month: int
    ) -> str:
        summary = await self.tx.monthly_summary(business_id, year, month)
        udhaar_out = await self.udhaar.outstanding_total(business_id, "customer")
        month_name = date(year, month, 1).strftime("%B")
        profit = summary["profit"]
        return f"""📊 *{business_name} — {month_name} {year} Summary*
━━━━━━━━━━━━━━━━━━━
💰 Total Sale: Rs. {summary['revenue']:,.0f}
💸 Total Kharcha: Rs. {summary['expenses']:,.0f}
📈 *Net Profit: Rs. {profit:,.0f}*
━━━━━━━━━━━━━━━━━━━
⚠️ Outstanding Udhaar: Rs. {udhaar_out:,.0f}
━━━━━━━━━━━━━━━━━━━

Excel report chahiye? "Excel bhejo" likhein."""
