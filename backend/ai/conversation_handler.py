import json
import logging
from datetime import date, datetime
from typing import Any

from ai.intent_classifier import classify_intent
from ai.ocr_processor import extract_from_receipt
from ai.transaction_extractor import extract_transaction
from ai.voice_processor import transcribe_voice
from core.database import get_supabase, run_db
from services.insight_service import InsightService
from services.invoice_service import InvoiceService
from services.report_service import ReportService
from services.transaction_service import TransactionService
from services.udhaar_service import UdhaarService
from services.user_service import UserService
from services.whatsapp import WhatsAppService
from utils.messages import CATEGORIES, MESSAGES
from utils.phone import normalize_phone

logger = logging.getLogger(__name__)

tx_service = TransactionService()
udhaar_service = UdhaarService()
invoice_service = InvoiceService()
report_service = ReportService()
insight_service = InsightService()
user_service = UserService()
wa_service = WhatsAppService()


def _db():
    return get_supabase()


async def save_state(user_phone: str, state: str | None, context: dict | None = None) -> None:
    phone = normalize_phone(user_phone)
    payload = {
        "user_phone": phone,
        "state": state,
        "context": context or {},
        "updated_at": datetime.utcnow().isoformat(),
    }

    await run_db(
        lambda: _db()
        .table("conversation_states")
        .upsert(payload, on_conflict="user_phone")
        .execute()
    )


async def clear_state(user_phone: str) -> None:
    await save_state(user_phone, None, {})


async def get_state(user_phone: str) -> tuple[str | None, dict]:
    phone = normalize_phone(user_phone)

    def _fetch() -> tuple[str | None, dict]:
        row = _db().table("conversation_states").select("*").eq("user_phone", phone).execute()
        if not row.data:
            return None, {}
        data = row.data[0]
        return data.get("state"), data.get("context") or {}

    return await run_db(_fetch)


async def log_message(user_phone: str, direction: str, content: str, msg_type: str = "text") -> None:
    try:
        await run_db(
            lambda: _db()
            .table("message_logs")
            .insert(
                {
                    "user_phone": normalize_phone(user_phone),
                    "direction": direction,
                    "message_type": msg_type,
                    "content": content[:2000],
                }
            )
            .execute()
        )
    except Exception as exc:
        logger.debug("Message log skipped: %s", exc)


def get_main_menu(business_name: str) -> str:
    return f"""*{business_name}* 📊

Kya karna chahte hain?

1️⃣ Sale add karo
2️⃣ Expense add karo
3️⃣ Invoice banao
4️⃣ Udhaar track karo
5️⃣ Report dekho
6️⃣ Excel report
7️⃣ Insights
8️⃣ Help / Menu"""


async def handle_message(user_phone: str, message: dict) -> str:
    phone = normalize_phone(user_phone)
    msg_type = message.get("type", "text")
    text = ""

    if msg_type == "text":
        text = message.get("text", {}).get("body", "").strip()
    elif msg_type == "audio":
        audio_id = message.get("audio", {}).get("id")
        text = await transcribe_voice(audio_id)
        if not text:
            return "Voice note samajh nahi aayi. Text mein likhein ya ENABLE_WHISPER=true karein."
        await log_message(phone, "inbound", f"[voice] {text}", "audio")
    elif msg_type == "image":
        image_id = message.get("image", {}).get("id")
        return await extract_from_receipt(image_id, phone)
    else:
        return "Sirf text, voice note, ya tasveer bhejein. 📱"

    await log_message(phone, "inbound", text, msg_type)
    user, business = await user_service.get_user_with_business(phone)

    if not user.get("onboarding_complete"):
        return await handle_onboarding(phone, user, text)

    state, context = await get_state(phone)
    if state:
        return await continue_flow(phone, user, business, text, state, context)

    text_lower = text.lower().strip()
    business_name = business["name"] if business else "Aapka Business"

    if text_lower in {"menu", "help", "8"} or text_lower == "kya kar sakte ho":
        return get_main_menu(business_name)

    if text_lower in {"1", "sale add", "sale"}:
        await save_state(phone, "awaiting_sale_text", {})
        return "Sale likhein, masalan: *Ahmed ko TV 45000 cash*"

    if text_lower in {"2", "expense add", "expense"}:
        await save_state(phone, "awaiting_expense_text", {})
        return "Expense likhein, masalan: *bijli bill 3500*"

    if text_lower in {"3", "invoice"}:
        await save_state(phone, "awaiting_invoice_customer", {})
        return "Invoice banana hai! ✅\n\nCustomer ka naam kya hai?"

    if text_lower in {"4", "udhaar"}:
        return (
            "Udhaar ke liye natural language likhein:\n"
            "• *Ahmed ko 5000 udhaar diya*\n"
            "• *supplier se 10000 maal udhaar par*\n"
            "• *Ahmed ne 2000 wapis diye*"
        )

    if text_lower in {"5", "report"}:
        return await handle_report_request(user, business)

    if text_lower in {"6", "excel bhejo", "excel", "sheet"}:
        return await handle_excel_request(phone, user, business)

    if text_lower in {"7", "insights"}:
        return await handle_insights(user, business)

    intent = await classify_intent(text)

    if intent == "sale":
        return await handle_sale(phone, user, business, text)
    if intent == "expense":
        return await handle_expense(phone, user, business, text)
    if intent == "invoice":
        await save_state(phone, "awaiting_invoice_customer", {"seed_text": text})
        return "Customer ka naam kya hai?"
    if intent == "udhaar_give":
        return await handle_udhaar_give(phone, user, business, text)
    if intent == "udhaar_receive":
        return await handle_udhaar_receive(phone, user, business, text)
    if intent == "udhaar_payment":
        return await handle_udhaar_payment(phone, user, business, text)
    if intent == "report":
        return await handle_report_request(user, business)
    if intent == "excel":
        return await handle_excel_request(phone, user, business)
    if intent == "insights":
        return await handle_insights(user, business)
    if intent == "help":
        return get_main_menu(business_name)

    return MESSAGES["unknown"]


async def handle_onboarding(phone: str, user: dict, text: str) -> str:
    state, context = await get_state(phone)
    if not state:
        await save_state(phone, "onboarding_name", {})
        return MESSAGES["welcome"]

    if state == "onboarding_name":
        context["business_name"] = text.strip()
        await save_state(phone, "onboarding_category", context)
        return MESSAGES["setup_category"]

    if state == "onboarding_category":
        choice = text.strip()
        cat = CATEGORIES.get(choice)
        if not cat:
            return "1 se 9 tak number select karein."
        context["category"], context["mode"] = cat
        await save_state(phone, "onboarding_phone", context)
        return "Invoice par kaunsa phone number show karna hai? (03001234567)"

    if state == "onboarding_phone":
        context["business_phone"] = text.strip()
        biz = await user_service.complete_onboarding(
            user["id"],
            context["business_name"],
            context["category"],
            context["mode"],
            context.get("business_phone"),
        )
        await clear_state(phone)
        return (
            f"✅ Setup complete! *{biz['name']}* ready hai.\n\n"
            + get_main_menu(biz["name"])
        )

    return MESSAGES["welcome"]


async def continue_flow(
    phone: str,
    user: dict,
    business: dict | None,
    text: str,
    state: str,
    context: dict,
) -> str:
    if not business:
        await clear_state(phone)
        return "Pehle onboarding complete karein. *menu* likhein."

    business_id = business["id"]
    text_lower = text.lower().strip()

    if state == "awaiting_sale_amount":
        amount = _parse_amount(text)
        if amount is None:
            return "Amount number mein likhein, masalan: 5000"
        await tx_service.create_transaction(
            business_id=business_id,
            type="sale",
            amount=amount,
            description=context.get("description", ""),
            customer_name=context.get("customer"),
            payment_method=context.get("payment_method", "cash"),
        )
        await clear_state(phone)
        monthly = await tx_service.get_monthly_total(business_id, "sale")
        return f"✅ Sale record! Rs. {amount:,.0f}\nIs mahine ki total sale: *Rs. {monthly:,.0f}*"

    if state == "awaiting_expense_amount":
        amount = _parse_amount(text)
        if amount is None:
            return "Amount number mein likhein."
        await tx_service.create_transaction(
            business_id=business_id,
            type="expense",
            amount=amount,
            description=context.get("description", ""),
            category=context.get("category", "other"),
            vendor_name=context.get("vendor"),
            payment_method=context.get("payment_method", "cash"),
        )
        await clear_state(phone)
        monthly = await tx_service.get_monthly_total(business_id, "expense")
        return f"✅ Expense record! Rs. {amount:,.0f}\nIs mahine ke kharche: *Rs. {monthly:,.0f}*"

    if state == "awaiting_sale_text":
        await clear_state(phone)
        return await handle_sale(phone, user, business, text)

    if state == "awaiting_expense_text":
        await clear_state(phone)
        return await handle_expense(phone, user, business, text)

    if state == "awaiting_invoice_customer":
        context["customer_name"] = text.strip()
        await save_state(phone, "awaiting_invoice_item", context)
        return "Item aur amount likhein (masalan: LED TV 45000)"

    if state == "awaiting_invoice_item":
        data = await extract_transaction(text, "sale")
        amount = data.get("amount")
        if not amount:
            await save_state(phone, "awaiting_invoice_amount", context)
            return "Item ka amount kitna hai?"
        context["items"] = [
            {
                "item_name": data.get("description") or "Item",
                "quantity": 1,
                "unit_price": float(amount),
            }
        ]
        await save_state(phone, "awaiting_invoice_payment", context)
        return """Payment method?
1️⃣ Cash  2️⃣ Bank  3️⃣ Easypaisa  4️⃣ JazzCash  5️⃣ Udhaar"""

    if state == "awaiting_invoice_amount":
        amount = _parse_amount(text)
        if amount is None:
            return "Valid amount likhein."
        context["items"] = [{"item_name": "Item", "quantity": 1, "unit_price": amount}]
        await save_state(phone, "awaiting_invoice_payment", context)
        return "Payment method? (1-5)"

    if state == "awaiting_invoice_payment":
        methods = {
            "1": "Cash",
            "2": "Bank Transfer",
            "3": "Easypaisa",
            "4": "JazzCash",
            "5": "Udhaar",
        }
        payment = methods.get(text.strip(), text.strip())
        inv = await invoice_service.create_invoice(
            business_id=business_id,
            customer_name=context["customer_name"],
            items=context["items"],
            payment_method=payment,
            business_name=business["name"],
            business_phone=business.get("phone") or "",
        )
        await clear_state(phone)
        if inv.get("pdf_url"):
            await wa_service.send_document(
                phone,
                inv["pdf_url"],
                f"{inv['invoice_number']}.pdf",
                f"Invoice {inv['invoice_number']}",
            )
        return (
            f"✅ *Invoice Ready!*\n🧾 #{inv['invoice_number']}\n"
            f"👤 {inv['customer_name']}\n💰 Rs. {float(inv['total_amount']):,.0f}\n"
            f"💳 {payment}"
        )

    if state == "confirm_pending_tx":
        if text_lower in {"1", "haan", "yes", "save"}:
            pending = context.get("pending_tx", {})
            await tx_service.create_transaction(**pending)
            await clear_state(phone)
            return "✅ Saved!"
        await clear_state(phone)
        return "Cancel ho gaya. *menu* likhein."

    if state == "awaiting_udhaar_party":
        amount = context.get("amount")
        if amount:
            await udhaar_service.create_record(
                business_id=business_id,
                party_name=text.strip(),
                party_type=context.get("party_type", "customer"),
                total_amount=float(amount),
            )
            await clear_state(phone)
            return f"✅ Udhaar record! {text.strip()} — Rs. {float(amount):,.0f}"
        return "Amount pehle batayein."

    await clear_state(phone)
    return MESSAGES["unknown"]


def _parse_amount(text: str) -> float | None:
    import re

    cleaned = text.replace(",", "").strip().lower()
    m = re.search(r"(\d+(?:\.\d+)?)\s*k", cleaned)
    if m:
        return float(m.group(1)) * 1000
    m = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    return float(m.group(1)) if m else None


async def handle_sale(
    phone: str, user: dict, business: dict | None, text: str
) -> str:
    if not business:
        return "Pehle business setup complete karein."
    data = await extract_transaction(text, "sale")
    amount = data.get("amount")
    if not amount:
        await save_state(
            phone,
            "awaiting_sale_amount",
            {
                "description": data.get("description"),
                "customer": data.get("customer_or_vendor"),
                "payment_method": data.get("payment_method", "cash"),
            },
        )
        return "Kitne ki sale hui? (amount likhein)"
    await tx_service.create_transaction(
        business_id=business["id"],
        type="sale",
        amount=float(amount),
        description=data.get("description") or "",
        customer_name=data.get("customer_or_vendor"),
        payment_method=data.get("payment_method", "cash"),
    )
    monthly = await tx_service.get_monthly_total(business["id"], "sale")
    return (
        f"✅ *Sale Record Ho Gayi!*\n\n"
        f"💰 Rs. {float(amount):,.0f}\n"
        f"📝 {data.get('description') or 'N/A'}\n"
        f"💳 {str(data.get('payment_method', 'cash')).title()}\n\n"
        f"Is mahine ki total sale: *Rs. {monthly:,.0f}*"
    )


async def handle_expense(
    phone: str, user: dict, business: dict | None, text: str
) -> str:
    if not business:
        return "Pehle business setup complete karein."
    data = await extract_transaction(text, "expense")
    amount = data.get("amount")
    if not amount:
        await save_state(
            phone,
            "awaiting_expense_amount",
            {
                "description": data.get("description"),
                "vendor": data.get("customer_or_vendor"),
                "category": data.get("category", "other"),
                "payment_method": data.get("payment_method", "cash"),
            },
        )
        return "Kitna kharcha hua? (amount likhein)"
    await tx_service.create_transaction(
        business_id=business["id"],
        type="expense",
        amount=float(amount),
        description=data.get("description") or "",
        category=data.get("category"),
        vendor_name=data.get("customer_or_vendor"),
        payment_method=data.get("payment_method", "cash"),
    )
    monthly = await tx_service.get_monthly_total(business["id"], "expense")
    return (
        f"✅ *Expense Record Ho Gaya!*\n\n"
        f"💸 Rs. {float(amount):,.0f}\n"
        f"📝 {data.get('description') or 'N/A'}\n\n"
        f"Is mahine ke kharche: *Rs. {monthly:,.0f}*"
    )


async def handle_udhaar_give(
    phone: str, user: dict, business: dict | None, text: str
) -> str:
    if not business:
        return "Business setup required."
    data = await extract_transaction(text, "sale")
    amount = data.get("amount")
    party = data.get("customer_or_vendor")
    if not amount:
        return "Udhaar ki amount clear likhein, masalan: Ahmed ko 5000 udhaar diya"
    if not party:
        await save_state(
            phone,
            "awaiting_udhaar_party",
            {"amount": amount, "party_type": "customer"},
        )
        return "Kis customer ko udhaar diya? Naam likhein."
    await udhaar_service.create_record(
        business_id=business["id"],
        party_name=party,
        party_type="customer",
        total_amount=float(amount),
    )
    return f"✅ Udhaar record! {party} — Rs. {float(amount):,.0f} (customer owes you)"


async def handle_udhaar_receive(
    phone: str, user: dict, business: dict | None, text: str
) -> str:
    if not business:
        return "Business setup required."
    data = await extract_transaction(text, "expense")
    amount = data.get("amount")
    party = data.get("customer_or_vendor") or "Supplier"
    if not amount:
        return "Amount likhein, masalan: supplier se 10000 maal udhaar par"
    await udhaar_service.create_record(
        business_id=business["id"],
        party_name=party,
        party_type="supplier",
        total_amount=float(amount),
    )
    return f"✅ Supplier udhaar record! {party} — Rs. {float(amount):,.0f}"


async def handle_udhaar_payment(
    phone: str, user: dict, business: dict | None, text: str
) -> str:
    if not business:
        return "Business setup required."
    data = await extract_transaction(text, "sale")
    amount = data.get("amount")
    party = (data.get("customer_or_vendor") or "").strip()
    if not amount or not party:
        return "Likhein: Ahmed ne 2000 de diye (naam + amount)"
    rows = await udhaar_service.list_by_business(business["id"], "customer")
    match = next(
        (r for r in rows if party.lower() in r["party_name"].lower()), None
    )
    if not match:
        return f"{party} ka udhaar record nahi mila."
    await udhaar_service.record_payment(match["id"], float(amount))
    balance = float(match["total_amount"]) - float(match.get("paid_amount", 0)) - float(amount)
    return f"✅ Payment record! {party} ne Rs. {float(amount):,.0f} diye. Baaki: Rs. {max(balance, 0):,.0f}"


async def handle_report_request(user: dict, business: dict | None) -> str:
    if not business:
        return "Business setup required."
    today = date.today()
    return await report_service.text_monthly_report(
        business["id"], business["name"], today.year, today.month
    )


async def handle_excel_request(
    phone: str, user: dict, business: dict | None
) -> str:
    if not business:
        return "Business setup required."
    today = date.today()
    content = await report_service.generate_excel_bytes(
        business["id"], business["name"], today.year, today.month
    )
    filename = f"hisaab-{today.year}-{today.month:02d}.xlsx"
    url = await report_service.upload_excel(business["id"], filename, content)
    if url:
        await wa_service.send_document(phone, url, filename, "Monthly Excel report 📊")
        return "Excel report bhej di! 📊"
    return "Excel generate ho gaya lekin upload fail. Dashboard se download karein."


async def handle_insights(user: dict, business: dict | None) -> str:
    if not business:
        return "Business setup required."
    return await insight_service.weekly_insights(business["id"], business["name"])
