import pytest

from parsing import parse_quantity, parse_value_jpy


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
