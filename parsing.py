import pandas as pd


def _is_blank(value) -> bool:
    if value is None:
        return True
    if not isinstance(value, str) and pd.isna(value):
        return True
    if isinstance(value, str):
        return value.strip() in ("", "-")
    return False


def _coalesce_series(primary: pd.Series, fallback: pd.Series) -> pd.Series:
    mask = ~primary.apply(_is_blank)
    return primary.where(mask, fallback)


def _normalize_number_input(value):
    if _is_blank(value):
        return None
    if isinstance(value, str):
        cleaned = value.strip()
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


def _normalize_header_name(header: object) -> str:
    text = str(header).strip()
    text = text.replace("（", "(").replace("）", ")")
    for whitespace in (" ", "　", "\t", "\n", "\r"):
        text = text.replace(whitespace, "")
    return text


def normalize_import_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [_normalize_header_name(col) for col in normalized.columns]

    rename_map = {
        "大分類": "major_category",
        "中分類": "sub_category",
        "口座区分": "account_type",
        "評価額(円)": "value_jpy",
    }
    for source, target in rename_map.items():
        if target not in normalized.columns and source in normalized.columns:
            normalized = normalized.rename(columns={source: target})

    if "name_or_ticker" not in normalized.columns:
        if "銘柄名" in normalized.columns and "ティッカー" in normalized.columns:
            normalized["name_or_ticker"] = _coalesce_series(
                normalized["銘柄名"], normalized["ティッカー"]
            )
        elif "銘柄名" in normalized.columns:
            normalized = normalized.rename(columns={"銘柄名": "name_or_ticker"})
        elif "ティッカー" in normalized.columns:
            normalized = normalized.rename(columns={"ティッカー": "name_or_ticker"})

    if "quantity" not in normalized.columns:
        if "保有数量" in normalized.columns:
            normalized = normalized.rename(columns={"保有数量": "quantity"})
        elif "保有数" in normalized.columns and "口数" in normalized.columns:
            normalized["quantity"] = _coalesce_series(
                normalized["保有数"], normalized["口数"]
            )
        elif "保有数" in normalized.columns:
            normalized = normalized.rename(columns={"保有数": "quantity"})
        elif "口数" in normalized.columns:
            normalized = normalized.rename(columns={"口数": "quantity"})

    return normalized
