from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.portfolio import Valuation
from app.schemas.valuations import ValuationCreate, ValuationRead

router = APIRouter(tags=["valuations"])


@router.post("/valuations", response_model=ValuationRead)
def create_valuation(payload: ValuationCreate, db: Session = Depends(get_db)) -> Valuation:
    valuation = Valuation(**payload.model_dump())
    db.add(valuation)
    db.commit()
    db.refresh(valuation)
    return valuation
