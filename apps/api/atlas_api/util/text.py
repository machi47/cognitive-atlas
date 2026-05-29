from __future__ import annotations

import re


COMMAND_RE = re.compile(r"^/([a-zA-Z][\w-]*)(?:\s+(.*))?$")


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()) * 4 // 3)


def first_sentence_title(text: str, fallback: str = "New chat") -> str:
    cleaned = normalize_whitespace(text)
    if not cleaned:
        return fallback
    sentence = re.split(r"(?<=[.!?])\s+", cleaned)[0]
    title = sentence[:70].strip()
    return title if title else fallback


def parse_command(text: str) -> tuple[str | None, str]:
    match = COMMAND_RE.match(text.strip())
    if not match:
        return None, text
    command = match.group(1).lower()
    rest = match.group(2) or ""
    return command, rest.strip()


def keywords_title(text: str) -> str:
    cleaned = normalize_whitespace(text).lower()
    if "substratecad" in cleaned or "substrate cad" in cleaned:
        return "substrateCAD"
    if "trace impedance" in cleaned or "signal integrity" in cleaned or "package substrate" in cleaned or "soc interconnect" in cleaned:
        return "Physical Signal Integrity"
    if "analog" in cleaned or "compute-in-memory" in cleaned or "compute in memory" in cleaned:
        return "Analog Compute"
    if "agent" in cleaned or "conversation plane" in cleaned:
        return "Learning Agent Architecture"
    words = [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", cleaned) if w not in STOPWORDS]
    if not words:
        return "Unsorted Thoughts"
    return " ".join(word.capitalize() for word in words[:3])


STOPWORDS = {
    "the",
    "and",
    "that",
    "this",
    "with",
    "from",
    "because",
    "about",
    "whether",
    "what",
    "when",
    "where",
    "have",
    "does",
    "into",
    "make",
    "think",
}
