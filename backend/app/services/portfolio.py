from __future__ import annotations

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.portfolio import Valuation
from app.models.taxonomies import InstrumentClassification, TargetAllocation, Taxonomy, TaxonomyNode
from app.services.calculations import calculate_allocation, calculate_deviation


def get_allocation(session: Session, as_of: date, taxonomy: str) -> list[dict]:
    rows = (
        session.query(
            TaxonomyNode.id,
            TaxonomyNode.name,
            func.sum(Valuation.value_jpy).label("value_jpy"),
        )
        .join(InstrumentClassification, InstrumentClassification.taxonomy_node_id == TaxonomyNode.id)
        .join(Valuation, Valuation.instrument_id == InstrumentClassification.instrument_id)
        .join(Taxonomy, Taxonomy.id == TaxonomyNode.taxonomy_id)
        .filter(Taxonomy.name == taxonomy, Valuation.valuation_date == as_of)
        .group_by(TaxonomyNode.id)
        .all()
    )
    values = {row.id: float(row.value_jpy or 0) for row in rows}
    weights = calculate_allocation(values)
    return [
        {
            "taxonomy_node_id": row.id,
            "taxonomy_node_name": row.name,
            "value_jpy": float(row.value_jpy or 0),
            "weight": weights.get(row.id, 0.0),
        }
        for row in rows
    ]


def get_deviation(session: Session, as_of: date, taxonomy: str) -> list[dict]:
    allocation = get_allocation(session, as_of, taxonomy)
    total_value = sum(item["value_jpy"] for item in allocation)
    actual_weights = {item["taxonomy_node_id"]: item["weight"] for item in allocation}
    targets = (
        session.query(TargetAllocation)
        .join(Taxonomy)
        .filter(Taxonomy.name == taxonomy)
        .all()
    )
    target_weights = {target.taxonomy_node_id: target.target_weight for target in targets}
    deviations = calculate_deviation(actual_weights, target_weights, total_value)
    nodes = (
        session.query(TaxonomyNode)
        .join(Taxonomy)
        .filter(Taxonomy.name == taxonomy)
        .all()
    )
    node_map = {node.id: node.name for node in nodes}
    response = []
    for node_id, metrics in deviations.items():
        response.append(
            {
                "taxonomy_node_id": node_id,
                "taxonomy_node_name": node_map.get(node_id, "Unknown"),
                **metrics,
            }
        )
    return response


def get_timeseries(session: Session, start: date, end: date, group_by: str) -> list[dict]:
    if group_by == "month":
        period_expr = func.strftime("%Y-%m", Valuation.valuation_date)
    else:
        period_expr = func.strftime("%Y-%m-%d", Valuation.valuation_date)

    rows = (
        session.query(period_expr.label("period"), func.sum(Valuation.value_jpy).label("total"))
        .filter(Valuation.valuation_date.between(start, end))
        .group_by("period")
        .order_by("period")
        .all()
    )
    return [{"period": row.period, "total_value_jpy": float(row.total or 0)} for row in rows]
