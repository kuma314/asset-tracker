from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.portfolio import AllocationItem, DeviationItem, TimeseriesPoint
from app.services.portfolio import get_allocation, get_deviation, get_timeseries

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio/allocation", response_model=list[AllocationItem])
def allocation(
    date: date = Query(..., alias="date"),
    taxonomy: str = "asset_class",
    db: Session = Depends(get_db),
):
    return get_allocation(db, date, taxonomy)


@router.get("/portfolio/deviation", response_model=list[DeviationItem])
def deviation(
    date: date = Query(..., alias="date"),
    taxonomy: str = "asset_class",
    db: Session = Depends(get_db),
):
    return get_deviation(db, date, taxonomy)


@router.get("/portfolio/timeseries", response_model=list[TimeseriesPoint])
def timeseries(
    start: date,
    end: date,
    group_by: str = "month",
    db: Session = Depends(get_db),
):
    return get_timeseries(db, start, end, group_by)
