from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class ContributionPlan(Base):
    __tablename__ = "contribution_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    monthly_amount = Column(Float, nullable=False)
    rebalance_mode = Column(String, nullable=False, default="target")
    is_active = Column(Integer, nullable=False, default=1)

    allocation_rules = relationship(
        "ContributionAllocationRule", back_populates="plan", cascade="all, delete-orphan"
    )


class ContributionAllocationRule(Base):
    __tablename__ = "contribution_allocation_rules"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("contribution_plans.id"), nullable=False)
    taxonomy_node_id = Column(Integer, ForeignKey("taxonomy_nodes.id"), nullable=False)
    weight = Column(Float, nullable=True)
    fixed_amount = Column(Float, nullable=True)

    plan = relationship("ContributionPlan", back_populates="allocation_rules")
    taxonomy_node = relationship("TaxonomyNode")
