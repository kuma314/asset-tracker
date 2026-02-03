from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    quantity = Column(Float, nullable=True)

    account = relationship("Account", back_populates="positions")
    instrument = relationship("Instrument", back_populates="positions")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    price_date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="JPY")

    instrument = relationship("Instrument", back_populates="prices")


class Valuation(Base):
    __tablename__ = "valuations"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True)
    valuation_date = Column(Date, nullable=False)
    value_jpy = Column(Float, nullable=False)

    account = relationship("Account", back_populates="valuations")
    instrument = relationship("Instrument", back_populates="valuations")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=True)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(String, nullable=False)
    quantity = Column(Float, nullable=True)
    amount_jpy = Column(Float, nullable=False)

    account = relationship("Account", back_populates="transactions")
    instrument = relationship("Instrument", back_populates="transactions")
