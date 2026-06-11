import re


def normalize_phone(phone: str) -> str:
    """Normalize to E.164-ish format (+digits only)."""
    cleaned = re.sub(r"[^\d+]", "", phone.strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    if not cleaned.startswith("+"):
        if cleaned.startswith("92"):
            cleaned = "+" + cleaned
        elif cleaned.startswith("0") and len(cleaned) == 11:
            cleaned = "+92" + cleaned[1:]
        elif len(cleaned) == 10:
            cleaned = "+1" + cleaned
        else:
            cleaned = "+" + cleaned
    return cleaned
