import hashlib
import hmac
import json
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from ai.conversation_handler import handle_message
from core.config import settings
from services.whatsapp import WhatsAppService

logger = logging.getLogger(__name__)
router = APIRouter()
wa_service = WhatsAppService()


def _verify_signature(body: bytes, signature: str | None) -> bool:
    if not settings.WHATSAPP_APP_SECRET:
        return True
    if not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(signature[7:], expected)


@router.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook/whatsapp")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not _verify_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {"status": "ok"}

    logger.info("Webhook POST received: %s", json.dumps(payload)[:500])

    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            # Status updates (delivered/read) — no reply needed
            logger.info("Webhook POST: no messages in payload (status update?)")
            return {"status": "ok"}

        message = messages[0]
        user_phone = message.get("from")
        if message.get("id"):
            background_tasks.add_task(wa_service.mark_as_read, message["id"])
        background_tasks.add_task(process_message, user_phone, message)
    except Exception as exc:
        logger.exception("Webhook parse error: %s", exc)

    return {"status": "ok"}


async def process_message(user_phone: str, message: dict):
    try:
        response_text = await handle_message(user_phone, message)
        if response_text:
            await wa_service.send_text(user_phone, response_text)
    except Exception as exc:
        logger.exception("Processing error for %s: %s", user_phone, exc)
        await wa_service.send_text(
            user_phone,
            "Kuch masla ho gaya 😔 Dobara try karein ya 'menu' likhein.",
        )
