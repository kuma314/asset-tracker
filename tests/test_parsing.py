from io import StringIO

import pandas as pd
import pytest

from parsing import normalize_import_dataframe, parse_quantity, parse_value_jpy


def test_parse_value_jpy_allows_commas() -> None:
    assert parse_value_jpy("601,652") == 601652


def test_parse_value_jpy_none_and_empty() -> None:
    assert parse_value_jpy(None) is None
    assert parse_value_jpy("") is None
    assert parse_value_jpy("-") is None
    assert parse_value_jpy(float("nan")) is None


def test_parse_value_jpy_negative_raises() -> None:
    with pytest.raises(ValueError):
        parse_value_jpy("-1")


def test_parse_quantity_commas_and_decimals() -> None:
    assert parse_quantity("211,866") == 211866.0
    assert parse_quantity("0.00482006") == 0.00482006


def test_parse_quantity_dash_and_empty() -> None:
    assert parse_quantity("-") is None
    assert parse_quantity("") is None


def test_normalize_import_dataframe_japanese_headers() -> None:
    source = pd.DataFrame(
        {
            "大分類": ["株式", "投信"],
            "中分類": ["国内", "海外"],
            "銘柄名": ["トヨタ", ""],
            "ティッカー": ["7203", "AAPL"],
            "口座区分": ["特定", "NISA"],
            "保有数": ["100", ""],
            "口数": ["", "10"],
            "評価額(円)": ["1,000", "2,000"],
        }
    )

    normalized = normalize_import_dataframe(source)

    assert normalized["major_category"].tolist() == ["株式", "投信"]
    assert normalized["sub_category"].tolist() == ["国内", "海外"]
    assert normalized["name_or_ticker"].tolist() == ["トヨタ", "AAPL"]
    assert normalized["account_type"].tolist() == ["特定", "NISA"]
    assert normalized["quantity"].tolist() == ["100", "10"]
    assert normalized["value_jpy"].tolist() == ["1,000", "2,000"]


def test_normalize_import_dataframe_japanese_headers_from_csv() -> None:
    csv_data = StringIO(
        " 大分類 ,中分類 ,銘柄名 , ティッカー ,口座区分 ,保有数量 ,評価額（円）\n"
        '株式,国内,トヨタ,7203,特定,"1,234.5","1,234"\n'
        '投信,海外,,AAPL,NISA,-,"2,000"\n'
    )
    source = pd.read_csv(csv_data)

    normalized = normalize_import_dataframe(source)

    assert normalized["major_category"].tolist() == ["株式", "投信"]
    assert normalized["sub_category"].tolist() == ["国内", "海外"]
    assert normalized["name_or_ticker"].tolist() == ["トヨタ", "AAPL"]
    assert normalized["account_type"].tolist() == ["特定", "NISA"]
    assert normalized["quantity"].tolist() == ["1,234.5", "-"]
    assert normalized["value_jpy"].tolist() == ["1,234", "2,000"]
