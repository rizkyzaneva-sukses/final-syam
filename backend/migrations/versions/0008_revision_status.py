"""Add review workflow without changing existing revision content or images."""
from alembic import op
import sqlalchemy as sa

revision = "0008_revision_status"
down_revision = "0007_revision_proposals"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("revision_proposals") as batch:
        batch.add_column(sa.Column("owner_role", sa.String(40), nullable=True))
        batch.add_column(sa.Column("status", sa.String(24), nullable=False, server_default="REVISI"))
        batch.add_column(sa.Column("status_note", sa.Text(), nullable=True))
        batch.add_column(sa.Column("status_updated_at", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("status_updated_by_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_revision_status_updated_by", "users", ["status_updated_by_id"], ["id"])
    connection = op.get_bind()
    rows = connection.execute(sa.text("""SELECT r.id, r.module_name, u.role
        FROM revision_proposals r JOIN users u ON u.id = r.reported_by_id"""))
    for row in rows:
        title = row.module_name.upper()
        explicit = (
            ("CMO SUPPORT", "CMO_SUPPORT"), ("CMO MANAGER", "CMO_MANAGER"),
            ("CFO MANAGER", "CFO_MANAGER"), ("COO MANAGER", "COO_MANAGER"),
            ("CHRO MANAGER", "CHRO_MANAGER"), ("HR SUPPORT", "HR_SUPPORT"),
            ("FINANCE SUPPORT", "FINANCE_SUPPORT"),
            ("PRINTING PIC", "PRINTING_PIC"), ("SAMPLE PIC", "SAMPLE_PIC"),
            ("PRODUCTION PIC", "PRODUCTION_PIC"),
        )
        owner = next((role for tag, role in explicit if tag in title), None)
        if owner is None:
            prefixes = (("CEO-", "CEO"), ("REF-CEO", "CEO"), ("HR-", "CHRO_MANAGER"),
                        ("REF-HR", "CHRO_MANAGER"), ("CFO-", "CFO_MANAGER"),
                        ("REF-LUTFI", "CFO_MANAGER"), ("COO-", "COO_MANAGER"),
                        ("REF-COO", "COO_MANAGER"), ("PRN-", "PRINTING_PIC"),
                        ("REF-IMAN", "PRINTING_PIC"), ("SMP-", "SAMPLE_PIC"),
                        ("REF-FAHRUL", "SAMPLE_PIC"), ("CMO-", "CMO_MANAGER"),
                        ("REF-CECEP", "CMO_MANAGER"), ("REF-DEBY", "CMO_SUPPORT"))
            owner = next((role for tag, role in prefixes if title.startswith(tag)), None)
        if owner is None:
            owner = row.role
        connection.execute(sa.text("UPDATE revision_proposals SET owner_role = :owner WHERE id = :id"),
                           {"owner": owner, "id": row.id})
    op.create_table(
        "revision_status_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proposal_id", sa.Integer(), sa.ForeignKey("revision_proposals.id"), nullable=False),
        sa.Column("from_status", sa.String(24), nullable=False),
        sa.Column("to_status", sa.String(24), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("changed_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_revision_status_events_proposal_id", "revision_status_events", ["proposal_id"])


def downgrade():
    raise RuntimeError("Revision status migration is forward-only; restore a verified backup into a separate database.")
