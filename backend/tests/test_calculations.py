import pytest

from app.services.calculations import calculate_allocation, calculate_deviation, forecast_values


def test_calculate_allocation() -> None:
    values = {1: 200, 2: 300}
    allocation = calculate_allocation(values)
    assert allocation[1] == 0.4
    assert allocation[2] == 0.6


def test_calculate_deviation() -> None:
    actual = {1: 0.4, 2: 0.6}
    target = {1: 0.5, 2: 0.5}
    result = calculate_deviation(actual, target, total_value=1000)
    assert result[1]["diff_weight_pp"] == pytest.approx(-0.1)
    assert result[1]["diff_value_jpy"] == pytest.approx(-100)
    assert result[2]["diff_weight_pp"] == pytest.approx(0.1)
    assert result[2]["diff_value_jpy"] == pytest.approx(100)


def test_forecast_values() -> None:
    values = forecast_values(start_value=1000, annual_return=0.12, monthly_contribution=100, months=2)
    assert values[0] == 1000
    assert values[1] == 1110.0
    assert values[2] == 1221.1
