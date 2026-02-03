from __future__ import annotations


def calculate_allocation(values_by_node: dict[int, float]) -> dict[int, float]:
    total = sum(values_by_node.values())
    if total == 0:
        return {node_id: 0.0 for node_id in values_by_node}
    return {node_id: value / total for node_id, value in values_by_node.items()}


def calculate_deviation(
    actual_weights: dict[int, float],
    target_weights: dict[int, float],
    total_value: float,
) -> dict[int, dict[str, float]]:
    nodes = set(actual_weights) | set(target_weights)
    deviations: dict[int, dict[str, float]] = {}
    for node_id in nodes:
        actual = actual_weights.get(node_id, 0.0)
        target = target_weights.get(node_id, 0.0)
        diff_weight = actual - target
        deviations[node_id] = {
            "actual_weight": actual,
            "target_weight": target,
            "diff_weight_pp": diff_weight,
            "diff_value_jpy": diff_weight * total_value,
        }
    return deviations


def forecast_values(
    start_value: float,
    annual_return: float,
    monthly_contribution: float,
    months: int,
) -> list[float]:
    values = [start_value]
    monthly_rate = annual_return / 12
    current = start_value
    for _ in range(months):
        current = current * (1 + monthly_rate) + monthly_contribution
        values.append(round(current, 2))
    return values
