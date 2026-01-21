import csv
from io import StringIO
from typing import Iterable

import pandas as pd


REPORT_ENCODING_CANDIDATES: tuple[str, ...] = ("cp932", "shift_jis", "utf-8")


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


def decode_csv_bytes(data: bytes) -> str:
    last_error: UnicodeDecodeError | None = None
    for encoding in REPORT_ENCODING_CANDIDATES:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise ValueError("CSVの文字コードを判定できませんでした。") from last_error


def detect_report_csv(data: bytes) -> tuple[bool, str]:
    decoded_candidates: list[str] = []
    for encoding in REPORT_ENCODING_CANDIDATES:
        try:
            decoded_text = data.decode(encoding)
        except UnicodeDecodeError:
            continue
        decoded_candidates.append(decoded_text)
        if _looks_like_report_csv(decoded_text):
            return True, decoded_text
    if not decoded_candidates:
        raise ValueError("CSVの文字コードを判定できませんでした。")
    return False, decoded_candidates[0]


def parse_report_csv(data: bytes) -> pd.DataFrame:
    is_report, decoded_text = detect_report_csv(data)
    if not is_report:
        raise ValueError("保有証券一覧レポート形式のCSVではありません。")
    return _parse_report_text(decoded_text)


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


def _looks_like_report_csv(text: str) -> bool:
    if "保有証券一覧" in text:
        return True
    normalized = _normalize_section_text(text)
    return "株式(" in normalized or "投資信託(金額/" in normalized


def _normalize_section_text(text: str) -> str:
    normalized = text.replace("（", "(").replace("）", ")")
    for whitespace in (" ", "　", "\t", "\n", "\r"):
        normalized = normalized.replace(whitespace, "")
    return normalized


def _parse_section_header(row: Iterable[str]) -> tuple[str, str | None] | None:
    first_non_blank = None
    for cell in row:
        if isinstance(cell, str) and cell.strip():
            first_non_blank = cell.strip()
            break
    if not first_non_blank:
        return None
    normalized = _normalize_section_text(first_non_blank)
    if normalized.startswith("株式("):
        return "株式", _extract_account_type(normalized)
    if normalized.startswith("投資信託("):
        return "投資信託", _extract_account_type(normalized)
    return None


def _extract_account_type(section_text: str) -> str | None:
    if "(" not in section_text or ")" not in section_text:
        return None
    inner = section_text.split("(", 1)[1].rsplit(")", 1)[0]
    if inner.startswith("金額/"):
        inner = inner.split("金額/", 1)[1]
    return inner or None


def _normalize_account_type(account_type: str | None) -> str | None:
    if not account_type:
        return None
    normalized = _normalize_section_text(account_type)
    mapping = {
        "NISA預り(成長投資枠)": "NISA(成長)",
        "NISA預り(つみたて投資枠)": "NISA(つみたて)",
        "旧つみたてNISA預り": "旧つみたてNISA",
    }
    for key, value in mapping.items():
        if key in normalized:
            return value
    return account_type.strip()


def _parse_header_row(
    row: Iterable[str],
    asset_type: str,
) -> dict[str, int] | None:
    headers = [_normalize_header_name(cell) for cell in row]
    if asset_type == "株式":
        required = {"銘柄コード", "銘柄名称", "保有株数", "評価額"}
    else:
        required = {"ファンド名", "保有口数", "評価額"}
    if not required.issubset(set(headers)):
        return None
    return {header: idx for idx, header in enumerate(headers)}


def _get_cell(row: list[str], idx: int) -> str:
    if idx < len(row):
        return row[idx]
    return ""


def _normalize_quantity_value(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.replace("口", "") if isinstance(value, str) else value
    return parse_quantity(cleaned)


def _parse_report_text(text: str) -> pd.DataFrame:
    reader = csv.reader(StringIO(text))
    rows: list[dict] = []
    current_asset: str | None = None
    current_account: str | None = None
    header_map: dict[str, int] | None = None
    include_section = False

    for row in reader:
        if not row or all(_is_blank(cell) for cell in row):
            continue

        section_info = _parse_section_header(row)
        if section_info is not None:
            current_asset, current_account = section_info
            header_map = None
            include_section = current_asset == "株式" or (
                current_asset == "投資信託"
                and current_account is not None
                and "NISA" in current_account
            )
            continue

        if current_asset is None:
            continue

        if header_map is None:
            header_map = _parse_header_row(row, current_asset)
            if header_map is not None:
                continue

        if header_map is None or not include_section:
            continue

        if current_asset == "株式":
            code = _get_cell(row, header_map["銘柄コード"]).strip()
            name = _get_cell(row, header_map["銘柄名称"]).strip()
            quantity = parse_quantity(_get_cell(row, header_map["保有株数"]))
        else:
            code = ""
            name = _get_cell(row, header_map["ファンド名"]).strip()
            quantity = _normalize_quantity_value(
                _get_cell(row, header_map["保有口数"])
            )

        value_jpy = parse_value_jpy(_get_cell(row, header_map["評価額"]))
        name_or_ticker = f"{code} {name}".strip()
        if not name_or_ticker or value_jpy is None:
            continue

        account_type = _normalize_account_type(current_account)
        rows.append(
            {
                "major_category": "日本株" if current_asset == "株式" else "投資信託",
                "sub_category": "株式" if current_asset == "株式" else "投資信託",
                "name_or_ticker": name_or_ticker,
                "account_type": account_type or "",
                "quantity": quantity,
                "value_jpy": value_jpy,
            }
        )

    return pd.DataFrame(rows)
