from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from core.database import get_supabase
from core.security import get_current_user_phone
from services.insight_service import InsightService
from services.invoice_service import InvoiceService
from services.report_service import ReportService
from services.transaction_service import TransactionService
from services.udhaar_service import UdhaarService
from services.user_service import UserService
from utils.phone import normalize_phone

router = APIRouter()
user_service = UserService()
tx_service = TransactionService()
udhaar_service = UdhaarService()
invoice_service = InvoiceService()
report_service = ReportService()
insight_service = InsightService()


async def _resolve_business(phone: str) -> tuple[dict, dict]:
    user, business = await user_service.get_user_with_business(phone)
    if not user.get("onboarding_complete") or not business:
        raise HTTPException(
            status_code=400,
            detail="Complete WhatsApp onboarding first (message your bot)",
        )
    return user, business


@router.get("/dashboard/summary")
async def dashboard_summary(
    phone: str = Depends(get_current_user_phone),
    month: int | None = None,
    year: int | None = None,
):
    _, business = await _resolve_business(phone)
    today = date.today()
    month = month or today.month
    year = year or today.year
    summary = await tx_service.monthly_summary(business["id"], year, month)
    udhaar_out = await udhaar_service.outstanding_total(business["id"], "customer")
    recent = await tx_service.list_transactions(business["id"], limit=10)
    top_udhaar = await udhaar_service.list_by_business(business["id"], "customer")
    top_udhaar = sorted(
        top_udhaar,
        key=lambda r: float(r["total_amount"]) - float(r.get("paid_amount", 0)),
        reverse=True,
    )[:5]
    return {
        "business": business,
        "summary": {**summary, "udhaar_outstanding": udhaar_out},
        "recent_transactions": recent,
        "top_udhaar": top_udhaar,
        "month": month,
        "year": year,
    }


@router.get("/transactions")
async def list_transactions(
    phone: str = Depends(get_current_user_phone),
    type: str | None = None,
    limit: int = Query(100, le=500),
):
    _, business = await _resolve_business(phone)
    return await tx_service.list_transactions(business["id"], type, limit)


@router.get("/udhaar")
async def list_udhaar(
    phone: str = Depends(get_current_user_phone),
    party_type: str | None = None,
):
    _, business = await _resolve_business(phone)
    return await udhaar_service.list_by_business(business["id"], party_type)


@router.get("/invoices")
async def list_invoices(phone: str = Depends(get_current_user_phone)):
    _, business = await _resolve_business(phone)
    return await invoice_service.list_invoices(business["id"])


@router.get("/reports/excel")
async def download_excel(
    phone: str = Depends(get_current_user_phone),
    month: int | None = None,
    year: int | None = None,
):
    from fastapi.responses import Response

    _, business = await _resolve_business(phone)
    today = date.today()
    month = month or today.month
    year = year or today.year
    content = await report_service.generate_excel_bytes(
        business["id"], business["name"], year, month
    )
    filename = f"hisaab-{year}-{month:02d}.xlsx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/insights")
async def get_insights(phone: str = Depends(get_current_user_phone)):
    _, business = await _resolve_business(phone)
    text = await insight_service.weekly_insights(business["id"], business["name"])
    return {"insights": text}


@router.get("/me")
async def get_me(phone: str = Depends(get_current_user_phone)):
    user, business = await user_service.get_user_with_business(phone)
    return {"user": user, "business": business, "phone": normalize_phone(phone)}
