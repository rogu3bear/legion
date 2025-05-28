"""Initial core schema migration

Revision ID: 001_initial_core
Revises:
Create Date: 2024-12-30 21:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001_initial_core'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial core database tables."""
    # Create schema_version table
    op.create_table('schema_version'
        sa.Column('version', sa.Integer(), nullable=False)
        sa.PrimaryKeyConstraint('version')
    )

    # Create agents table
    op.create_table('agents'
        sa.Column('id', sa.Integer(), nullable=False)
        sa.Column('name', sa.String(), nullable=False)
        sa.Column('type', sa.String(), nullable=False)
        sa.Column('status', sa.String(), nullable=False)
        sa.Column('capabilities', sa.String(), nullable=True)
        sa.Column('config', sa.String(), nullable=True)
        sa.Column('agent_metadata', sa.String(), nullable=True)
        sa.Column('is_active', sa.Boolean(), nullable=True)
        sa.Column('last_heartbeat', sa.DateTime(), nullable=True)
        sa.Column('created_at', sa.DateTime(), nullable=False)
        sa.Column('updated_at', sa.DateTime(), nullable=False)
        sa.PrimaryKeyConstraint('id')
        sa.UniqueConstraint('name')
    )

    # Create tasks table
    op.create_table('tasks'
        sa.Column('id', sa.Integer(), nullable=False)
        sa.Column('agent_id', sa.Integer(), nullable=False)
        sa.Column('type', sa.String(), nullable=False)
        sa.Column('status', sa.String(), nullable=False)
        sa.Column('priority', sa.String(), nullable=False)
        sa.Column('title', sa.String(), nullable=False)
        sa.Column('description', sa.String(), nullable=True)
        sa.Column('task_data', sa.String(), nullable=True)
        sa.Column('result_data', sa.String(), nullable=True)
        sa.Column('error_message', sa.String(), nullable=True)
        sa.Column('created_at', sa.DateTime(), nullable=False)
        sa.Column('updated_at', sa.DateTime(), nullable=False)
        sa.Column('started_at', sa.DateTime(), nullable=True)
        sa.Column('completed_at', sa.DateTime(), nullable=True)
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], )
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_agents_status', 'agents', ['status'])
    op.create_index('idx_agents_type', 'agents', ['type'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_agent_id', 'tasks', ['agent_id'])


def downgrade() -> None:
    """Drop all core database tables."""
    op.drop_index('idx_tasks_agent_id', table_name='tasks')
    op.drop_index('idx_tasks_priority', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')
    op.drop_index('idx_agents_type', table_name='agents')
    op.drop_index('idx_agents_status', table_name='agents')
    op.drop_table('tasks')
    op.drop_table('agents')
    op.drop_table('schema_version')
