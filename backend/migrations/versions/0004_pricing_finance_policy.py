"""Store reviewable per-article pricing and explicit G1 payment terms."""
from alembic import op
import sqlalchemy as sa

revision = "0004_pricing_finance_policy"
down_revision = "0003_integrity_reconciliation"
branch_labels = None
depends_on = None


def upgrade():
    for column in (
        sa.Column("finance_term_kind", sa.String(20), nullable=True),
        sa.Column("required_dp_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("payment_evidence_ref", sa.Text(), nullable=True),
        sa.Column("credit_due_date", sa.Date(), nullable=True),
    ):
        op.add_column("orders", column)
    for column in (
        sa.Column("pricing_breakdown", sa.Text(), nullable=True),
        sa.Column("hpp_total", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("margin_amount", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("margin_percent", sa.Numeric(8, 2), nullable=False, server_default="0"),
        sa.Column("payment_plan", sa.Text(), nullable=True),
        sa.Column("approval_reason", sa.Text(), nullable=True),
        sa.Column("approved_by_id", sa.Integer(), nullable=True),
        sa.Column("ceo_approved_by_id", sa.Integer(), nullable=True),
        sa.Column("ceo_approval_reason", sa.Text(), nullable=True),
    ):
        op.add_column("quotations", column)
    with op.batch_alter_table("quotations") as batch:
        batch.create_foreign_key("fk_quotations_approved_by_id", "users", ["approved_by_id"], ["id"])
        batch.create_foreign_key("fk_quotations_ceo_approved_by_id", "users", ["ceo_approved_by_id"], ["id"])


def downgrade():
    raise RuntimeError("Pricing migration is forward-only; restore a verified backup into a separate database.")
