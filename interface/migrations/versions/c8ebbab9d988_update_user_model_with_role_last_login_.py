"""Update User model with role, last_login, and renamed password hash

Revision ID: c8ebbab9d988
Revises: 0c41691da765
Create Date: 2025-04-22 17:15:30.857556
"""

import sqlalchemy as sa
from alembic import op

revision = "c8ebbab9d988"
down_revision = "0c41691da765"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_preferences",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("theme", sa.String(length=50), nullable=False),
        sa.Column("notifications_enabled", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.add_column(
        "users", sa.Column("password_hash", sa.String(length=200), nullable=False)
    )
    op.add_column("users", sa.Column("role", sa.String(length=50), nullable=False))
    op.add_column("users", sa.Column("last_login", sa.DateTime(), nullable=True))
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.drop_column("users", "hashed_password")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users", sa.Column("hashed_password", sa.VARCHAR(length=200), nullable=False)
    )
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_column("users", "last_login")
    op.drop_column("users", "role")
    op.drop_column("users", "password_hash")
    op.drop_table("user_preferences")
