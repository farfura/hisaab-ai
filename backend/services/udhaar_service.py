from datetime import date
from typing import Any

from core.database import get_supabase


class UdhaarService:
    async def create_record(
        self,
        business_id: str,
        party_name: str,
        party_type: str,
        total_amount: float,
        party_phone: str | None = None,
        due_date: date | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        db = get_supabase()
        payload = {
            "business_id": business_id,
            "party_name": party_name,
            "party_type": party_type,
            "total_amount": total_amount,
            "paid_amount": 0,
            "party_phone": party_phone,
            "due_date": due_date.isoformat() if due_date else None,
            "status": "pending",
            "notes": notes,
        }
        result = db.table("udhaar_records").insert(payload).execute()
        return result.data[0]

    async def record_payment(
        self, udhaar_id: str, amount: float, payment_method: str = "cash"
    ) -> dict[str, Any]:
        db = get_supabase()
        record = db.table("udhaar_records").select("*").eq("id", udhaar_id).execute()
        if not record.data:
            raise ValueError("Udhaar record not found")
        row = record.data[0]
        new_paid = float(row["paid_amount"]) + amount
        total = float(row["total_amount"])
        status = "paid" if new_paid >= total else "partial" if new_paid > 0 else "pending"

        db.table("udhaar_payments").insert(
            {
                "udhaar_id": udhaar_id,
                "amount": amount,
                "payment_method": payment_method,
            }
        ).execute()

        updated = (
            db.table("udhaar_records")
            .update({"paid_amount": new_paid, "status": status})
            .eq("id", udhaar_id)
            .execute()
        )
        return updated.data[0]

    async def list_by_business(
        self, business_id: str, party_type: str | None = None
    ) -> list[dict[str, Any]]:
        db = get_supabase()
        query = db.table("udhaar_records").select("*").eq("business_id", business_id)
        if party_type:
            query = query.eq("party_type", party_type)
        return query.order("created_at", desc=True).execute().data

    async def outstanding_total(self, business_id: str, party_type: str = "customer") -> float:
        rows = await self.list_by_business(business_id, party_type)
        total = 0.0
        for row in rows:
            if row.get("status") != "paid":
                total += float(row["total_amount"]) - float(row.get("paid_amount", 0))
        return total
