from __future__ import annotations

import re
import unicodedata

_INDEX_SUFFIX_RE = re.compile(r"(インデックス(?:\s*ファンド)?|インデックスファンド)$")
_ALL_COUNTRY_RE = re.compile(r"[（(]?オール[\s・-]*カントリー[)）]?")
_SPACE_RE = re.compile(r"\s+")
_MIDDLE_DOT_RE = re.compile(r"[・･·/／]")
_DASH_RE = re.compile(r"[－‐‑–—―−]")


def canonicalize_name(value: object | None) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.replace("＆", "&").replace("＋", "+")
    text = _MIDDLE_DOT_RE.sub(" ", text)
    text = _DASH_RE.sub("-", text)
    text = _SPACE_RE.sub(" ", text).strip()
    text = text.upper()

    if "EMAXIS SLIM" in text and "全世界株式" in text:
        text = _ALL_COUNTRY_RE.sub("", text)

    text = _SPACE_RE.sub(" ", text).strip()
    text = _INDEX_SUFFIX_RE.sub("", text).strip()
    text = _SPACE_RE.sub(" ", text).strip()
    return text


def canonical_name(value: object | None) -> str:
    return canonicalize_name(value)
