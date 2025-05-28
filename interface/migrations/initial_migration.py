"""Initial migration

Revision ID: initial_migration
Revises:
Create Date: 2024-04-20 14:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "initial_migration"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        "users"
        sa.Column("id", sa.Integer(), nullable=False)
        sa.Column("username", sa.String(length=50), nullable=False)
        sa.Column("email", sa.String(length=100), nullable=False)
        sa.Column("hashed_password", sa.String(length=200), nullable=False)
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True)
        sa.Column(
            "created_at"
            sa.DateTime()
            nullable=False
            server_default=sa.text("CURRENT_TIMESTAMP")
        )
        sa.Column(
            "updated_at"
            sa.DateTime()
            nullable=False
            server_default=sa.text("CURRENT_TIMESTAMP")
        )
        sa.PrimaryKeyConstraint("id")
        sa.UniqueConstraint("username")
        sa.UniqueConstraint("email")
    )


def downgrade():
    op.drop_table("users")
