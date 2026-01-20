import pandas as pd


def parse_value_jpy(value) -> int | None:
    if value is None:
        return None
    if not isinstance(value, str) and pd.isna(value):
        return None
    if value == "":
        return None
    if isinstance(value, str):
        value = value.replace(",", "").strip()
        if value == "":
            return None
    value_int = int(value)
    if value_int < 0:
        raise ValueError("value_jpy must be 0 or greater")
    return value_int
