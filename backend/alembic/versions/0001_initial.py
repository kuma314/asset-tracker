"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("account_type", sa.String(), nullable=False),
        sa.Column("institution", sa.String(), nullable=True),
    )
    op.create_table(
        "instruments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("ticker", sa.String(), nullable=True),
        sa.Column("instrument_type", sa.String(), nullable=False),
    )
    op.create_table(
        "taxonomies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
    )
    op.create_table(
        "taxonomy_nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("taxonomy_id", sa.Integer(), sa.ForeignKey("taxonomies.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("taxonomy_nodes.id"), nullable=True),
        sa.Column("equity_segment", sa.String(), nullable=True),
    )
    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
    )
    op.create_table(
        "prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id"), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False, server_default="JPY"),
    )
    op.create_table(
        "valuations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id"), nullable=True),
        sa.Column("position_id", sa.Integer(), sa.ForeignKey("positions.id"), nullable=True),
        sa.Column("valuation_date", sa.Date(), nullable=False),
        sa.Column("value_jpy", sa.Float(), nullable=False),
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id"), nullable=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("transaction_type", sa.String(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("amount_jpy", sa.Float(), nullable=False),
    )
    op.create_table(
        "instrument_classifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id"), nullable=False),
        sa.Column("taxonomy_node_id", sa.Integer(), sa.ForeignKey("taxonomy_nodes.id"), nullable=False),
    )
    op.create_table(
        "target_allocations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("taxonomy_id", sa.Integer(), sa.ForeignKey("taxonomies.id"), nullable=False),
        sa.Column("taxonomy_node_id", sa.Integer(), sa.ForeignKey("taxonomy_nodes.id"), nullable=False),
        sa.Column("target_weight", sa.Float(), nullable=False),
    )
    op.create_table(
        "contribution_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("monthly_amount", sa.Float(), nullable=False),
        sa.Column("rebalance_mode", sa.String(), nullable=False, server_default="target"),
        sa.Column("is_active", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_table(
        "contribution_allocation_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("contribution_plans.id"), nullable=False),
        sa.Column("taxonomy_node_id", sa.Integer(), sa.ForeignKey("taxonomy_nodes.id"), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("fixed_amount", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("contribution_allocation_rules")
    op.drop_table("contribution_plans")
    op.drop_table("target_allocations")
    op.drop_table("instrument_classifications")
    op.drop_table("transactions")
    op.drop_table("valuations")
    op.drop_table("prices")
    op.drop_table("positions")
    op.drop_table("taxonomy_nodes")
    op.drop_table("taxonomies")
    op.drop_table("instruments")
    op.drop_table("accounts")
