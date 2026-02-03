from datetime import date

from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.accounts import Account
from app.models.contributions import ContributionPlan
from app.models.instruments import Instrument
from app.models.portfolio import Valuation
from app.models.taxonomies import InstrumentClassification, TargetAllocation, Taxonomy, TaxonomyNode


def seed(session: Session) -> None:
    account = Account(name="Main Brokerage", account_type="brokerage", institution="Demo")
    instrument = Instrument(name="Global Equity Fund", ticker="GEF", instrument_type="fund")
    taxonomy = Taxonomy(name="asset_class")
    node_equity = TaxonomyNode(name="Equity", taxonomy=taxonomy, equity_segment="core")
    node_cash = TaxonomyNode(name="Cash", taxonomy=taxonomy)
    session.add_all([account, instrument, taxonomy, node_equity, node_cash])
    session.flush()

    session.add(InstrumentClassification(instrument_id=instrument.id, taxonomy_node_id=node_equity.id))
    session.add(TargetAllocation(taxonomy_id=taxonomy.id, taxonomy_node_id=node_equity.id, target_weight=0.7))
    session.add(TargetAllocation(taxonomy_id=taxonomy.id, taxonomy_node_id=node_cash.id, target_weight=0.3))

    session.add(
        Valuation(
            account_id=account.id,
            instrument_id=instrument.id,
            valuation_date=date.today(),
            value_jpy=5_000_000,
        )
    )
    session.add(
        Valuation(
            account_id=account.id,
            valuation_date=date.today(),
            value_jpy=1_000_000,
        )
    )
    session.add(
        ContributionPlan(
            name="Monthly Savings",
            start_date=date.today(),
            monthly_amount=100_000,
        )
    )


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed(session)
        session.commit()
