import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from core.config import settings

logger = logging.getLogger(__name__)

VALID_INTENTS = {
    "sale",
    "expense",
    "invoice",
    "udhaar_give",
    "udhaar_receive",
    "udhaar_payment",
    "report",
    "excel",
    "insights",
    "help",
    "unknown",
}

INTENT_PROMPT = ChatPromptTemplate.from_template(
    """You are an intent classifier for a Pakistani business accounting WhatsApp bot.

Classify the following message into EXACTLY ONE of these categories:
sale, expense, invoice, udhaar_give, udhaar_receive, udhaar_payment, report, excel, insights, help, unknown

Message: {message}

Reply with ONLY the category name."""
)


def _get_llm() -> ChatGroq:
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0,
        max_tokens=50,
    )


def _rule_based_intent(message: str) -> str | None:
    text = message.lower().strip()
    if text in {"menu", "help", "kya kar sakte ho", "?" }:
        return "help"
    if "excel" in text:
        return "excel"
    if "invoice" in text or "bill banao" in text:
        return "invoice"
    if "report" in text or "summary" in text or "kitna hua" in text:
        return "report"
    if "insight" in text or "trend" in text:
        return "insights"
    if "udhaar" in text and ("diya" in text or "di" in text):
        return "udhaar_give"
    if "udhaar" in text and ("liya" in text or "mila" in text or "receive" in text):
        return "udhaar_receive"
    if "udhaar" in text and ("de di" in text or "payment" in text or "wapis" in text):
        return "udhaar_payment"
    if any(w in text for w in ("sale", "mila", "aya", "becha", "sold")):
        return "sale"
    if any(w in text for w in ("expense", "kharcha", "khareeda", "bill", "gaya")):
        return "expense"
    return None


async def classify_intent(message: str) -> str:
    ruled = _rule_based_intent(message)
    if ruled:
        return ruled

    if not settings.GROQ_API_KEY:
        return "unknown"

    try:
        chain = INTENT_PROMPT | _get_llm() | StrOutputParser()
        result = (await chain.ainvoke({"message": message})).strip().lower()
        return result if result in VALID_INTENTS else "unknown"
    except Exception as exc:
        logger.warning("Intent classification error: %s", exc)
        return "unknown"
