import uuid
from datetime import date
from typing import Any

from core.config import settings
from core.database import get_supabase
from generators.pdf_invoice import generate_invoice_pdf


class InvoiceService:
    async def next_invoice_number(self, business_id: str) -> str:
        db = get_supabase()
        rows = (
            db.table("invoices")
            .select("invoice_number")
            .eq("business_id", business_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if not rows.data:
            return "INV-001"
        last = rows.data[0]["invoice_number"]
        try:
            num = int(last.split("-")[-1]) + 1
        except ValueError:
            num = 1
        return f"INV-{num:03d}"

    async def create_invoice(
        self,
        business_id: str,
        customer_name: str,
        items: list[dict[str, Any]],
        payment_method: str = "cash",
        customer_phone: str | None = None,
        business_name: str = "Business",
        business_phone: str = "",
    ) -> dict[str, Any]:
        subtotal = sum(float(i["quantity"]) * float(i["unit_price"]) for i in items)
        invoice_number = await self.next_invoice_number(business_id)
        db = get_supabase()

        invoice_row = {
            "business_id": business_id,
            "invoice_number": invoice_number,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "subtotal": subtotal,
            "total_amount": subtotal,
            "payment_method": payment_method,
            "payment_status": "unpaid" if payment_method.lower() == "udhaar" else "paid",
            "invoice_date": date.today().isoformat(),
        }
        inv = db.table("invoices").insert(invoice_row).execute().data[0]

        for item in items:
            qty = float(item.get("quantity", 1))
            price = float(item["unit_price"])
            db.table("invoice_items").insert(
                {
                    "invoice_id": inv["id"],
                    "item_name": item["item_name"],
                    "quantity": qty,
                    "unit_price": price,
                    "total_price": qty * price,
                }
            ).execute()

        pdf_bytes = generate_invoice_pdf(
            {
                "invoice_number": invoice_number,
                "business_name": business_name,
                "business_phone": business_phone,
                "customer_name": customer_name,
                "items": [
                    {
                        "name": i["item_name"],
                        "qty": float(i.get("quantity", 1)),
                        "price": float(i["unit_price"]),
                    }
                    for i in items
                ],
                "payment_method": payment_method,
                "date": date.today().strftime("%Y-%m-%d"),
            }
        )

        pdf_url = await self._upload_pdf(business_id, invoice_number, pdf_bytes)
        if pdf_url:
            db.table("invoices").update({"pdf_url": pdf_url}).eq("id", inv["id"]).execute()
            inv["pdf_url"] = pdf_url

        return inv

    async def _upload_pdf(
        self, business_id: str, invoice_number: str, pdf_bytes: bytes
    ) -> str | None:
        if not settings.SUPABASE_URL:
            return None
        db = get_supabase()
        path = f"{business_id}/{invoice_number}-{uuid.uuid4().hex[:8]}.pdf"
        bucket = settings.SUPABASE_STORAGE_BUCKET
        try:
            db.storage.from_(bucket).upload(
                path,
                pdf_bytes,
                {"content-type": "application/pdf", "upsert": "true"},
            )
            signed = db.storage.from_(bucket).create_signed_url(path, 60 * 60 * 24 * 7)
            return signed.get("signedURL") or signed.get("signedUrl")
        except Exception:
            return None

    async def list_invoices(self, business_id: str, limit: int = 50) -> list[dict[str, Any]]:
        db = get_supabase()
        return (
            db.table("invoices")
            .select("*")
            .eq("business_id", business_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
            .data
        )
