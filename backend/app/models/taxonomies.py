from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    nodes = relationship("TaxonomyNode", back_populates="taxonomy", cascade="all, delete-orphan")


class TaxonomyNode(Base):
    __tablename__ = "taxonomy_nodes"

    id = Column(Integer, primary_key=True)
    taxonomy_id = Column(Integer, ForeignKey("taxonomies.id"), nullable=False)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("taxonomy_nodes.id"), nullable=True)
    equity_segment = Column(String, nullable=True)

    taxonomy = relationship("Taxonomy", back_populates="nodes")
    children = relationship("TaxonomyNode")


class InstrumentClassification(Base):
    __tablename__ = "instrument_classifications"

    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), nullable=False)
    taxonomy_node_id = Column(Integer, ForeignKey("taxonomy_nodes.id"), nullable=False)

    instrument = relationship("Instrument", back_populates="classifications")
    taxonomy_node = relationship("TaxonomyNode")


class TargetAllocation(Base):
    __tablename__ = "target_allocations"

    id = Column(Integer, primary_key=True)
    taxonomy_id = Column(Integer, ForeignKey("taxonomies.id"), nullable=False)
    taxonomy_node_id = Column(Integer, ForeignKey("taxonomy_nodes.id"), nullable=False)
    target_weight = Column(Float, nullable=False)

    taxonomy = relationship("Taxonomy")
    taxonomy_node = relationship("TaxonomyNode")
