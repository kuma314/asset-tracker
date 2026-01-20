import pandas as pd


def _normalize_number_input(value):
    if value is None:
        return None
    if not isinstance(value, str) and pd.isna(value):
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned in ("", "-"):
            return None
        cleaned = cleaned.replace(",", "").strip()
        if cleaned in ("", "-"):
            return None
        return cleaned
    return value


def parse_value_jpy(value) -> int | None:
    normalized = _normalize_number_input(value)
    if normalized is None:
        return None
    value_int = int(normalized)
    if value_int < 0:
        raise ValueError("value_jpy must be 0 or greater")
    return value_int


def parse_quantity(value) -> float | None:
    normalized = _normalize_number_input(value)
    if normalized is None:
        return None
    return float(normalized)
