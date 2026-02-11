"""add orders

Revision ID: 44b5e3aff917
Revises: 48c414be4328
Create Date: 2026-02-09 02:59:57.680449

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "44b5e3aff917"
down_revision: Union[str, Sequence[str], None] = "48c414be4328"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("items", sa.JSON(), nullable=False),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "PAID", "SHIPPED", "CANCELED", name="order_status"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["orders.users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="orders",
    )
    op.create_index(op.f("ix_orders_orders_user_id"), "orders", ["user_id"], unique=False, schema="orders")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_orders_orders_user_id"), table_name="orders", schema="orders")
    op.drop_table("orders", schema="orders")
    # ### end Alembic commands ###
