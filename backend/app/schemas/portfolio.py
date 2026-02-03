from pydantic import BaseModel


class AllocationItem(BaseModel):
    taxonomy_node_id: int
    taxonomy_node_name: str
    value_jpy: float
    weight: float


class DeviationItem(BaseModel):
    taxonomy_node_id: int
    taxonomy_node_name: str
    actual_weight: float
    target_weight: float
    diff_weight_pp: float
    diff_value_jpy: float


class TimeseriesPoint(BaseModel):
    period: str
    total_value_jpy: float


class ForecastScenario(BaseModel):
    label: str
    values: list[float]
