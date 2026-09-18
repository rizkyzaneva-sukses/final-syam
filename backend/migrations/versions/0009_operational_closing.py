"""Require a separate COO operational close for future order closings.

Historical closed orders retain their recorded final state; the new operational
column labels them LEGACY_UNVERIFIED so they are not presented as COO approvals.
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_operational_closing"
down_revision = "0008_revision_status"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("orders") as batch:
        batch.add_column(sa.Column("operational_close_status", sa.String(32), nullable=False, server_default="OPEN"))
    with op.batch_alter_table("order_closings") as batch:
        batch.add_column(sa.Column("operational_close_status", sa.String(32), nullable=False, server_default="OPEN"))
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE order_closings SET operational_close_status = 'LEGACY_UNVERIFIED' WHERE order_close_status = 'CLOSED'"))
    connection.execute(sa.text("UPDATE orders SET operational_close_status = 'LEGACY_UNVERIFIED' WHERE overall_status = 'CLOSED'"))


def downgrade():
    raise RuntimeError("Operational closing migration is forward-only; restore a verified backup into a separate database.")
