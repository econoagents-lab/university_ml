from __future__ import annotations

import re
from dataclasses import dataclass

PII_PATTERNS = {
    "dni": re.compile(r"\b\d{8}\b"),
    "phone_pe": re.compile(r"\b9\d{8}\b"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "credential_hint": re.compile(r"(?i)(password|secret|token|api[_-]?key|redshift_password)\s*[:=]\s*\S+"),
}

INJECTION_PATTERNS = [
    re.compile(r"(?i)ignora\s+(tus|las)\s+instrucciones"),
    re.compile(r"(?i)ignore\s+(previous|all)\s+instructions"),
    re.compile(r"(?i)revela\s+(credenciales|password|token|secretos)"),
    re.compile(r"(?i)show\s+(credentials|password|token|secrets)"),
]

SENSITIVE_REQUEST_PATTERNS = [
    re.compile(r"(?i)\bDNI\b|documento\s+de\s+identidad"),
    re.compile(r"(?i)credenciales|password|token|secretos|api\s*key"),
]


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str
    sanitized_text: str


def mask_pii(text: str) -> str:
    """
    Yo enmascaro información sensible antes de indexar o responder.
    """
    sanitized = text
    sanitized = PII_PATTERNS["email"].sub("[EMAIL_MASKED]", sanitized)
    sanitized = PII_PATTERNS["phone_pe"].sub("[PHONE_MASKED]", sanitized)
    sanitized = PII_PATTERNS["dni"].sub("[DNI_MASKED]", sanitized)
    sanitized = PII_PATTERNS["credential_hint"].sub("[CREDENTIAL_MASKED]", sanitized)
    return sanitized


def detect_prompt_injection(text: str) -> bool:
    """
    Yo detecto instrucciones maliciosas que intentan romper las reglas del asistente.
    """
    return any(pattern.search(text or "") for pattern in INJECTION_PATTERNS)


def is_sensitive_request(question: str) -> bool:
    """
    Yo identifico preguntas que piden PII, credenciales o secretos.
    """
    return any(pattern.search(question or "") for pattern in SENSITIVE_REQUEST_PATTERNS)


def apply_input_guardrails(question: str) -> GuardrailResult:
    """
    Yo bloqueo preguntas inseguras antes de recuperar contexto.
    """
    if detect_prompt_injection(question):
        return GuardrailResult(False, "prompt_injection_detected", "")
    if is_sensitive_request(question):
        return GuardrailResult(False, "sensitive_request_detected", "")
    return GuardrailResult(True, "ok", mask_pii(question))


def sanitize_context(text: str) -> str:
    """
    Yo limpio cada fragmento recuperado para que el RAG no exponga datos sensibles.
    """
    return mask_pii(text)
