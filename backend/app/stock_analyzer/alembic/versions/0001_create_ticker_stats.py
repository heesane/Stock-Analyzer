from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_create_ticker_stats"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ticker_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticker", sa.String(length=32), nullable=False, unique=True),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_ticker_stats_ticker", "ticker_stats", ["ticker"], unique=True)


def downgrade() -> None:
    op.drop_table("ticker_stats")
