"""Adopt existing legacy tables without dropping or rewriting user data."""
from alembic import op
from sqlalchemy import inspect
from migrations.legacy_schema import Base

revision = "0001_legacy_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    inspector = inspect(connection)
    # A partial/unknown schema needs operator review rather than destructive guessing.
    for table in Base.metadata.sorted_tables:
        if inspector.has_table(table.name):
            actual = {c["name"] for c in inspector.get_columns(table.name)}
            missing = set(table.c.keys()) - actual
            if missing:
                raise RuntimeError(f"Legacy table {table.name} is missing columns: {sorted(missing)}")
    Base.metadata.create_all(connection, checkfirst=True)


def downgrade():
    raise RuntimeError("Baseline adoption cannot be downgraded; restore a verified backup into a separate database.")
