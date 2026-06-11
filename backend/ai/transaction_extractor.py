import json
import logging
import re

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from core.config import settings

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = ChatPromptTemplate.from_template(
    """Extract transaction information from this Pakistani business message.
Message may be Urdu, Roman Urdu, English, or mixed.

Transaction type: {transaction_type}
Message: {message}

Return ONLY valid JSON:
{{
  "amount": <number or null>,
  "description": "<string or null>",
  "customer_or_vendor": "<string or null>",
  "payment_method": "cash|bank_transfer|easypaisa|jazzcash|udhaar|unknown",
  "quantity": <number or null>,
  "category": "inventory|utilities|rent|salary|food|transport|other|null"
}}"""
)


def _parse_amount_from_text(message: str) -> float | None:
    text = message.lower().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*k\b", text)
    if match:
        return float(match.group(1)) * 1000
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        return float(match.group(1))
    return None


async def extract_transaction(message: str, transaction_type: str) -> dict:
    if not settings.GROQ_API_KEY:
        return {
            "amount": _parse_amount_from_text(message),
            "description": message[:120],
            "customer_or_vendor": None,
            "payment_method": "unknown",
            "category": "other",
        }

    try:
        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0,
            max_tokens=300,
        )
        chain = EXTRACTION_PROMPT | llm | JsonOutputParser()
        return await chain.ainvoke(
            {"message": message, "transaction_type": transaction_type}
        )
    except Exception as exc:
        logger.warning("Extraction error: %s", exc)
        raw = str(exc)
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass
        return {
            "amount": _parse_amount_from_text(message),
            "description": None,
            "customer_or_vendor": None,
            "payment_method": "unknown",
        }
