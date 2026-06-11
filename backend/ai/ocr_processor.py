import logging
import os
import tempfile

from ai.transaction_extractor import extract_transaction
from core.config import settings
from services.whatsapp import WhatsAppService

logger = logging.getLogger(__name__)
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr

        _reader = easyocr.Reader(["en", "ur"], gpu=False)
    return _reader


async def extract_from_receipt(image_id: str, user_phone: str) -> str:
    if not settings.ENABLE_OCR:
        return "Receipt OCR abhi band hai. Text mein amount likhein, masalan: 'expense 2500'."

    wa = WhatsAppService()
    image_bytes = await wa.download_media(image_id)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name
    try:
        results = _get_reader().readtext(tmp_path)
        extracted = " ".join(t for _, t, conf in results if conf > 0.3)
        if not extracted.strip():
            return "Tasveer mein text nahi mili. Clear photo bhejein. 📸"

        data = await extract_transaction(f"Receipt text: {extracted}", "expense")
        amount = data.get("amount")
        amount_text = f"Rs. {float(amount):,.0f}" if amount else "Amount nahi mili"
        return f"""📸 Receipt scan ho gayi!

📝 {data.get('description', 'Receipt items')}
💰 Total: {amount_text}

Expense record karoon?
1️⃣ Haan, save karo
2️⃣ Nahi"""
    except Exception as exc:
        logger.error("OCR error: %s", exc)
        return "Receipt scan fail ho gaya. Dobara try karein."
    finally:
        os.unlink(tmp_path)
