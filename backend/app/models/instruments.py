from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ticker = Column(String, nullable=True)
    instrument_type = Column(String, nullable=False)

    classifications = relationship(
        "InstrumentClassification", back_populates="instrument", cascade="all, delete-orphan"
    )
    positions = relationship("Position", back_populates="instrument", cascade="all, delete-orphan")
    prices = relationship("Price", back_populates="instrument", cascade="all, delete-orphan")
    valuations = relationship("Valuation", back_populates="instrument", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="instrument", cascade="all, delete-orphan")
