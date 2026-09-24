import re
import unicodedata


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower()).strip("-")


def stable_id(category: str, name: str) -> str:
    return f"{slug(category)}__{slug(name)}"


def name_key(name: str) -> str:
    return slug(name)