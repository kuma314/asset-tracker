from pydantic import BaseModel


class ForecastRequest(BaseModel):
    horizon_months: int
    annual_return: float
    monthly_contribution: float
    include_scenarios: bool = False
    scenario_delta: float = 0.01


class ForecastResponse(BaseModel):
    start_value: float
    scenarios: list[dict]
