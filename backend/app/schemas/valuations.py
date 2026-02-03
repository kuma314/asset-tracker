from datetime import date

from pydantic import BaseModel


class ValuationCreate(BaseModel):
    account_id: int
    instrument_id: int | None = None
    position_id: int | None = None
    valuation_date: date
    value_jpy: float


class ValuationRead(ValuationCreate):
    id: int

    class Config:
        from_attributes = True
