import logging

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self) -> None:
        self.base_url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}"
        self.phone_id = settings.WHATSAPP_PHONE_ID
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }

    async def send_text(self, to: str, text: str) -> None:
        if not settings.WHATSAPP_TOKEN or not self.phone_id:
            logger.warning("WhatsApp not configured; would send to %s: %s", to, text[:80])
            return
        chunks = _split_message(text)
        async with httpx.AsyncClient(timeout=30.0) as client:
            for chunk in chunks:
                response = await client.post(
                    f"{self.base_url}/{self.phone_id}/messages",
                    headers=self.headers,
                    json={
                        "messaging_product": "whatsapp",
                        "to": to,
                        "type": "text",
                        "text": {"body": chunk},
                    },
                )
                if response.status_code >= 400:
                    logger.error(
                        "WhatsApp send failed (%s) to %s: %s",
                        response.status_code,
                        to,
                        response.text,
                    )
                else:
                    logger.info("WhatsApp message sent to %s", to)

    async def send_document(
        self, to: str, file_url: str, filename: str, caption: str = ""
    ) -> None:
        if not settings.WHATSAPP_TOKEN or not self.phone_id:
            return
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.post(
                f"{self.base_url}/{self.phone_id}/messages",
                headers=self.headers,
                json={
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "document",
                    "document": {
                        "link": file_url,
                        "filename": filename,
                        "caption": caption,
                    },
                },
            )

    async def mark_as_read(self, message_id: str) -> None:
        if not settings.WHATSAPP_TOKEN or not self.phone_id:
            return
        async with httpx.AsyncClient(timeout=15.0) as client:
            await client.post(
                f"{self.base_url}/{self.phone_id}/messages",
                headers=self.headers,
                json={
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message_id,
                },
            )

    async def download_media(self, media_id: str) -> bytes:
        async with httpx.AsyncClient(timeout=60.0) as client:
            meta = await client.get(
                f"{self.base_url}/{media_id}",
                headers=self.headers,
            )
            meta.raise_for_status()
            media_url = meta.json()["url"]
            file_resp = await client.get(media_url, headers=self.headers)
            file_resp.raise_for_status()
            return file_resp.content


def _split_message(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    while text:
        parts.append(text[:limit])
        text = text[limit:]
    return parts
