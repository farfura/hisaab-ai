import logging
import os
import tempfile

from core.config import settings
from services.whatsapp import WhatsAppService

logger = logging.getLogger(__name__)
_model = None


def _get_model():
    global _model
    if _model is None:
        import whisper

        _model = whisper.load_model("small")
    return _model


async def transcribe_voice(audio_id: str) -> str:
    if not settings.ENABLE_WHISPER:
        return ""
    wa = WhatsAppService()
    audio_bytes = await wa.download_media(audio_id)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        result = _get_model().transcribe(tmp_path, language="ur", task="transcribe", fp16=False)
        return result["text"].strip()
    except Exception as exc:
        logger.error("Whisper error: %s", exc)
        return ""
    finally:
        os.unlink(tmp_path)
