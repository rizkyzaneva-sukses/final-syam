"""Collect revision proposals and optional screenshots from authenticated users."""
from alembic import op
import sqlalchemy as sa

revision = "0007_revision_proposals"
down_revision = "0006_full_cost_review"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "revision_proposals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module_name", sa.String(120), nullable=False),
        sa.Column("bug_description", sa.Text(), nullable=False),
        sa.Column("expected_behavior", sa.Text(), nullable=False),
        sa.Column("image_data", sa.LargeBinary(), nullable=True),
        sa.Column("image_mime", sa.String(40), nullable=True),
        sa.Column("reported_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_revision_proposals_reported_by_id", "revision_proposals", ["reported_by_id"])


def downgrade():
    raise RuntimeError("Revision proposal migration is forward-only; restore a verified backup into a separate database.")
