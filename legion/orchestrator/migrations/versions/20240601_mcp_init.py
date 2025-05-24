"""create mcp tables"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20240601_mcp_init"
down_revision = "20240520_task_registry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mcp_services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "mcp_tool_invocation_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("mcp_services.id")),
        sa.Column("tool_name", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("mcp_tool_invocation_log")
    op.drop_table("mcp_services")
