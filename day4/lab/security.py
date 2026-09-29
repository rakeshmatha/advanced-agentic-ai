"""Heuristic, offline GenAI security controls for Day 4 (IN08).

These checks are demonstrations, not authorization controls or guarantees that
attacks will be detected. Enforce access at the application/data boundary.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass


class ContentBlocked(ValueError):
    """Raised when a local moderation rule blocks a request or response."""


@dataclass(frozen=True)
class SecurityInspection:
    blocked: bool
    findings: tuple[str, ...]


_INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("instruction_override", re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I)),
    ("system_prompt_request", re.compile(r"(reveal|show|print|repeat).{0,30}(system|hidden)\s+prompt", re.I)),
    ("role_override", re.compile(r"\b(system|developer)\s*:\s*", re.I)),
)
_JAILBREAK_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("dan_persona", re.compile(r"\bact\s+as\s+(dan|an?\s+unrestricted\s+model)\b", re.I)),
    ("safety_override", re.compile(r"(disable|bypass|ignore)\s+(all\s+)?(safety|guardrails|restrictions)", re.I)),
    ("developer_mode", re.compile(r"\bdeveloper\s+mode\b", re.I)),
)
_EXFILTRATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(dump|export|reveal|list).{0,40}(all\s+)?(customer|user|account)\s+data", re.I),
    re.compile(r"(show|reveal|print).{0,30}(api\s+key|secret|credentials|system\s+prompt)", re.I),
)
_MODERATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:fuck|shit)\b", re.I),
    re.compile(r"\byou are stupid\b", re.I),
)
_PII_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("CARD", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")),
    ("SSN", re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")),
    ("EMAIL", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    (
        "PHONE",
        re.compile(r"(?<!\w)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\w)"),
    ),
)
_ZERO_WIDTH_OR_BIDI = {
    "\u200b", "\u200c", "\u200d", "\ufeff", "\u202a", "\u202b",
    "\u202c", "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069",
}


def inspect_prompt(text: str) -> SecurityInspection:
    """Flag common direct-injection and hidden Unicode indicators."""
    findings = [name for name, pattern in _INJECTION_PATTERNS if pattern.search(text)]
    if any(character in _ZERO_WIDTH_OR_BIDI for character in text):
        findings.append("invisible_or_bidi_unicode")
    return SecurityInspection(bool(findings), tuple(findings))


def inspect_jailbreak(text: str) -> SecurityInspection:
    findings = [name for name, pattern in _JAILBREAK_PATTERNS if pattern.search(text)]
    return SecurityInspection(bool(findings), tuple(findings))


def mask_pii(text: str, *, replacement: str = "[REDACTED:{kind}]") -> str:
    """Mask common email, phone, SSN, and payment-card-like values."""
    masked = text
    for kind, pattern in _PII_PATTERNS:
        masked = pattern.sub(lambda _match, label=kind: replacement.format(kind=label), masked)
    return masked


def contains_pii(text: str) -> bool:
    return mask_pii(text) != text


def safe_hash(text: str) -> str:
    """Return a one-way SHA-256 digest suitable for correlation, not recovery."""
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def safe_audit_payload(*, user_id: str, prompt: str, response: str, status: str) -> dict[str, str]:
    """Build an audit record without retaining raw identifiers or content."""
    return {
        "user_hash": safe_hash(user_id),
        "prompt_hash": safe_hash(prompt),
        "response_hash": safe_hash(response),
        "status": status,
    }


def sanitize_untrusted_tool_output(text: str) -> str:
    """Encode tool/RAG text as a JSON string so it remains data, not instructions."""
    return "UNTRUSTED_TOOL_DATA_JSON=" + json.dumps(text, ensure_ascii=True)


def inspect_exfiltration(text: str, *, max_output_chars: int = 8_000) -> SecurityInspection:
    """Heuristically flag secret/data-dump requests and suspiciously huge output."""
    findings = [
        f"exfiltration_pattern_{index}"
        for index, pattern in enumerate(_EXFILTRATION_PATTERNS, start=1)
        if pattern.search(text)
    ]
    if len(text) > max_output_chars:
        findings.append("output_size_limit")
    if re.search(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{160,}={0,2}(?![A-Za-z0-9+/])", text):
        findings.append("base64_like_payload")
    return SecurityInspection(bool(findings), tuple(findings))


def moderate_text(text: str) -> None:
    """Apply a tiny local moderation deny-list; raise ``ContentBlocked`` on match."""
    if any(pattern.search(text) for pattern in _MODERATION_PATTERNS):
        raise ContentBlocked("content matched the local demo moderation policy")


def has_control_characters(text: str) -> bool:
    """Return true for control characters other than ordinary whitespace."""
    return any(unicodedata.category(character) == "Cc" and character not in "\n\r\t" for character in text)
