"""Evidence-backed labor and overhead entries with CFO cost review."""
from alembic import op
import sqlalchemy as sa

revision = "0006_full_cost_review"
down_revision = "0005_bom_actual_cost"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "production_cost_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("article_id", sa.Integer(), sa.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("evidence_ref", sa.Text(), nullable=False),
        sa.Column("recorded_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_production_cost_entries_article_id", "production_cost_entries", ["article_id"])
    op.create_table(
        "cost_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_fk", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("reviewed_total", sa.Numeric(18, 2), nullable=False),
        sa.Column("evidence_ref", sa.Text(), nullable=False),
        sa.Column("reviewed_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    raise RuntimeError("Cost migration is forward-only; restore a verified backup into a separate database.")
