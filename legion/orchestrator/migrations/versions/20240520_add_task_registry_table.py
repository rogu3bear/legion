"""create task registry table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20240520_task_registry"
down_revision = "c8ebbab9d988"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "task_registry"
        sa.Column("id", sa.String(), primary_key=True)
        sa.Column("tags", sa.JSON(), nullable=False, server_default="[]")
        sa.Column("owner", sa.String(), nullable=False)
        sa.Column("agent", sa.String(), nullable=True)
        sa.Column("status", sa.String(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table("task_registry")
