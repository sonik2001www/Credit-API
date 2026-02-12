"""Initial schema

Revision ID: 202402121200
Revises: 
Create Date: 2026-02-13
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "202402121200"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dictionary",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("login", sa.String(length=50), nullable=False, unique=True),
        sa.Column("registration_date", sa.Date(), nullable=False),
    )

    op.create_table(
        "credits",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issuance_date", sa.Date(), nullable=False),
        sa.Column("return_date", sa.Date(), nullable=False),
        sa.Column("actual_return_date", sa.Date(), nullable=True),
        sa.Column("body", sa.Numeric(12, 2), nullable=False),
        sa.Column("percent", sa.Numeric(12, 2), nullable=False),
    )

    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("period", sa.Date(), nullable=False),
        sa.Column("sum", sa.Numeric(14, 2), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("dictionary.id"), nullable=False),
        sa.UniqueConstraint("period", "category_id", name="uq_plan_period_category"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sum", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("credit_id", sa.Integer(), sa.ForeignKey("credits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type_id", sa.Integer(), sa.ForeignKey("dictionary.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("plans")
    op.drop_table("credits")
    op.drop_table("users")
    op.drop_table("dictionary")
