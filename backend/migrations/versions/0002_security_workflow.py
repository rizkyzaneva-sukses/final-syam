"""Add approval evidence, stable links, and revocable authentication."""
from alembic import op
import sqlalchemy as sa

revision = "0002_security_workflow"
down_revision = "0001_legacy_baseline"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    additions = {
        "orders": [
            sa.Column("customer_id", sa.Integer(), nullable=True),
            sa.Column("finance_gate_status", sa.String(32), nullable=False, server_default="PENDING"),
            sa.Column("finance_gate_notes", sa.Text(), nullable=True),
            sa.Column("finance_verified_by_id", sa.Integer(), nullable=True),
        ],
        "production_movements": [sa.Column("reject_reason", sa.Text(), nullable=True)],
        "sample_records": [sa.Column("customer_approved_by_id", sa.Integer(), nullable=True)],
        "spks": [
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("snapshot", sa.Text(), nullable=True),
        ],
        "payments": [sa.Column("invoice_id", sa.Integer(), nullable=True)],
        "shipments": [
            sa.Column("packing_status", sa.String(32), nullable=False, server_default="PENDING"),
            sa.Column("finance_assessed_by_id", sa.Integer(), nullable=True),
            sa.Column("approved_outstanding", sa.Numeric(18, 2), nullable=True),
        ],
    }
    for table, columns in additions.items():
        existing = {c["name"] for c in sa.inspect(connection).get_columns(table)}
        for column in columns:
            if column.name not in existing:
                op.add_column(table, column)
    foreign_keys = [
        ("orders", "customer_id", "customers"),
        ("orders", "finance_verified_by_id", "users"),
        ("sample_records", "customer_approved_by_id", "users"),
        ("payments", "invoice_id", "invoices"),
        ("shipments", "finance_assessed_by_id", "users"),
    ]
    # SQLite needs batch recreation for constraints; values and rows are preserved.
    for table, column, target in foreign_keys:
        existing = sa.inspect(connection).get_foreign_keys(table)
        if not any(fk["constrained_columns"] == [column] for fk in existing):
            with op.batch_alter_table(table) as batch:
                batch.create_foreign_key(f"fk_{table}_{column}", target, [column], ["id"])
    if not sa.inspect(connection).has_table("auth_sessions"):
        op.create_table("auth_sessions",
            sa.Column("token_id", sa.String(64), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False))
        op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
        op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
    if not sa.inspect(connection).has_table("login_attempts"):
        op.create_table("login_attempts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("key", sa.String(64), nullable=False),
            sa.Column("attempted_at", sa.DateTime(), nullable=False))
        op.create_index("ix_login_attempts_key", "login_attempts", ["key"])
        op.create_index("ix_login_attempts_attempted_at", "login_attempts", ["attempted_at"])
    # Stable identity only where there is exactly one match. Never infer approval.
    connection.execute(sa.text("""
        UPDATE orders SET customer_id = (SELECT MIN(customers.id) FROM customers WHERE customers.name = orders.buyer)
        WHERE customer_id IS NULL AND (SELECT COUNT(*) FROM customers WHERE customers.name = orders.buyer) = 1
    """))
    connection.execute(sa.text("""
        UPDATE payments SET invoice_id = (SELECT MIN(invoices.id) FROM invoices WHERE invoices.invoice_no = payments.invoice_no)
        WHERE invoice_id IS NULL AND (SELECT COUNT(*) FROM invoices WHERE invoices.invoice_no = payments.invoice_no) = 1
    """))
    # Legacy paid_amount is intentionally retained; no synthetic payments or approvals.


def downgrade():
    raise RuntimeError("This safety migration is forward-only; restore a verified backup into a separate database.")
