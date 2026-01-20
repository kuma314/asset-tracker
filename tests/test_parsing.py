import pytest

from parsing import parse_value_jpy


def test_parse_value_jpy_allows_commas() -> None:
    assert parse_value_jpy("601,652") == 601652


def test_parse_value_jpy_none_and_empty() -> None:
    assert parse_value_jpy(None) is None
    assert parse_value_jpy("") is None
    assert parse_value_jpy(float("nan")) is None


def test_parse_value_jpy_negative_raises() -> None:
    with pytest.raises(ValueError):
        parse_value_jpy("-1")
