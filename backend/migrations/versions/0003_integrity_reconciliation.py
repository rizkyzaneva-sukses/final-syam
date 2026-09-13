"""Link historical inspections to articles and expose invoice ledger differences."""
from alembic import op
import sqlalchemy as sa

revision = "0003_integrity_reconciliation"
down_revision = "0002_security_workflow"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    for table in ("sample_records", "qc_records"):
        op.add_column(table, sa.Column("article_id", sa.Integer(), nullable=True))
        op.create_index(f"ix_{table}_article_id", table, ["article_id"])
        with op.batch_alter_table(table) as batch:
            batch.create_foreign_key(f"fk_{table}_article_id", "articles", ["article_id"], ["id"])
        connection.execute(sa.text(f"""
            UPDATE {table} SET article_id = (
                SELECT MIN(a.id) FROM articles a
                WHERE a.order_fk = {table}.order_fk AND a.article_code = {table}.article_code
            ) WHERE (SELECT COUNT(*) FROM articles a
                WHERE a.order_fk = {table}.order_fk AND a.article_code = {table}.article_code) = 1
        """))
    op.add_column("qc_records", sa.Column("rework_parent_id", sa.Integer(), nullable=True))
    with op.batch_alter_table("qc_records") as batch:
        batch.create_foreign_key("fk_qc_records_rework_parent_id", "qc_records", ["rework_parent_id"], ["id"])

    op.add_column("invoices", sa.Column("opening_paid_amount", sa.Numeric(18, 2), nullable=False, server_default="0"))
    op.add_column("invoices", sa.Column("reconciliation_status", sa.String(32), nullable=False, server_default="VERIFIED"))
    op.add_column("invoices", sa.Column("reconciliation_evidence", sa.Text(), nullable=True))
    op.add_column("invoices", sa.Column("reconciled_by_id", sa.Integer(), nullable=True))
    with op.batch_alter_table("invoices") as batch:
        batch.create_foreign_key("fk_invoices_reconciled_by_id", "users", ["reconciled_by_id"], ["id"])
    # Opening balance is displayed as a discrepancy, never invented as a payment.
    connection.execute(sa.text("""
        UPDATE invoices SET opening_paid_amount = CASE
            WHEN paid_amount > COALESCE((SELECT SUM(p.amount) FROM payments p
                WHERE p.invoice_id = invoices.id OR (p.invoice_id IS NULL AND p.invoice_no = invoices.invoice_no)), 0)
            THEN paid_amount - COALESCE((SELECT SUM(p.amount) FROM payments p
                WHERE p.invoice_id = invoices.id OR (p.invoice_id IS NULL AND p.invoice_no = invoices.invoice_no)), 0)
            ELSE 0 END
    """))
    connection.execute(sa.text("""
        UPDATE invoices SET reconciliation_status = CASE
            WHEN paid_amount < COALESCE((SELECT SUM(p.amount) FROM payments p
                WHERE p.invoice_id = invoices.id OR (p.invoice_id IS NULL AND p.invoice_no = invoices.invoice_no)), 0)
            THEN 'MISMATCH'
            WHEN opening_paid_amount > 0 THEN 'NEEDS_REVIEW'
            ELSE 'VERIFIED' END
    """))


def downgrade():
    raise RuntimeError("Integrity migration is forward-only; restore a verified backup into a separate database.")
