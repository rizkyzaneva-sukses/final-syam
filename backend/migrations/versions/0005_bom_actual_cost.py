"""Article BOM and evidenced material consumption."""
from alembic import op
import sqlalchemy as sa

revision = "0005_bom_actual_cost"
down_revision = "0004_pricing_finance_policy"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bom_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("article_id", sa.Integer(), sa.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("material_name", sa.String(200), nullable=False),
        sa.Column("unit", sa.String(40), nullable=False),
        sa.Column("qty_per_unit", sa.Numeric(12, 4), nullable=False),
        sa.Column("planned_unit_cost", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("article_id", "material_name", "unit", name="uq_bom_article_material_unit"),
    )
    op.create_index("ix_bom_items_article_id", "bom_items", ["article_id"])
    op.create_table(
        "material_consumptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bom_item_id", sa.Integer(), sa.ForeignKey("bom_items.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("qty", sa.Numeric(12, 4), nullable=False),
        sa.Column("actual_unit_cost", sa.Numeric(18, 2), nullable=False),
        sa.Column("evidence_ref", sa.Text(), nullable=False),
        sa.Column("recorded_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_material_consumptions_bom_item_id", "material_consumptions", ["bom_item_id"])


def downgrade():
    raise RuntimeError("BOM migration is forward-only; restore a verified backup into a separate database.")
