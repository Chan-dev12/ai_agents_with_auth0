import re
import uuid


# Patterns for common PII types. Order matters: more specific patterns first.
PII_PATTERNS = [
    ("EMAIL", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    ("PHONE", r"\b\d{10}\b"),
    ("SSN", r"\b\d{3}-\d{2}-\d{4}\b"),
    ("CARD", r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
]


def mask_sensitive_data(text: str) -> tuple[str, dict]:
    """
    Replace sensitive values (email, phone, etc.) with placeholder tokens
    before the text is sent to the LLM. Returns (masked_text, mapping) where
    mapping lets you restore the real values afterward for authorized viewers.
    """
    mapping: dict[str, str] = {}

    def make_masker(label: str):
        def masker(match: re.Match) -> str:
            token = f"[{label}_{uuid.uuid4().hex[:6]}]"
            mapping[token] = match.group(0)
            return token
        return masker

    for label, pattern in PII_PATTERNS:
        text = re.sub(pattern, make_masker(label), text)

    return text, mapping


def unmask_sensitive_data(text: str, mapping: dict) -> str:
    """
    Restore real values in the final response, for authorized viewers only.
    Call this AFTER the LLM has generated its response, never before.
    """
    for token, real_value in mapping.items():
        text = text.replace(token, real_value)
    return text