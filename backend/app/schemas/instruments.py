from pydantic import BaseModel


class InstrumentCreate(BaseModel):
    name: str
    ticker: str | None = None
    instrument_type: str


class InstrumentRead(InstrumentCreate):
    id: int

    class Config:
        from_attributes = True
