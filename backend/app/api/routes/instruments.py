from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.instruments import Instrument
from app.schemas.instruments import InstrumentCreate, InstrumentRead

router = APIRouter(tags=["instruments"])


@router.post("/instruments", response_model=InstrumentRead)
def create_instrument(payload: InstrumentCreate, db: Session = Depends(get_db)) -> Instrument:
    instrument = Instrument(**payload.model_dump())
    db.add(instrument)
    db.commit()
    db.refresh(instrument)
    return instrument
