from fastapi import APIRouter

from app.schemas.simulations import ForecastRequest, ForecastResponse
from app.services.calculations import forecast_values

router = APIRouter(tags=["simulations"])


@router.post("/simulations/forecast", response_model=ForecastResponse)
def forecast(payload: ForecastRequest) -> ForecastResponse:
    base_values = forecast_values(
        start_value=0,
        annual_return=payload.annual_return,
        monthly_contribution=payload.monthly_contribution,
        months=payload.horizon_months,
    )
    scenarios = [{"label": "base", "values": base_values}]
    if payload.include_scenarios:
        optimistic = forecast_values(
            start_value=0,
            annual_return=payload.annual_return + payload.scenario_delta,
            monthly_contribution=payload.monthly_contribution,
            months=payload.horizon_months,
        )
        pessimistic = forecast_values(
            start_value=0,
            annual_return=payload.annual_return - payload.scenario_delta,
            monthly_contribution=payload.monthly_contribution,
            months=payload.horizon_months,
        )
        scenarios.extend(
            [
                {"label": "optimistic", "values": optimistic},
                {"label": "pessimistic", "values": pessimistic},
            ]
        )
    return ForecastResponse(start_value=0, scenarios=scenarios)
