from __future__ import annotations

from rules import RULES


def apply_classification_rules(
    canonical_key: str,
    major_category: str | None,
    sub_category: str | None,
    name_or_ticker: str | None = None,
) -> tuple[str | None, str | None, str | None, bool]:
    for pattern, major, sub, display_name in RULES:
        if hasattr(pattern, "match"):
            if pattern.match(canonical_key):
                return major, sub, display_name or name_or_ticker, True
        elif canonical_key == pattern:
            return major, sub, display_name or name_or_ticker, True

    return major_category, sub_category, name_or_ticker, False
