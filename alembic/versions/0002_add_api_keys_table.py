"""Add api_keys table

Revision ID: 0002
Revises: 0001
Create Date: 2025-09-25 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('application', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    
    # Create indexes for better performance
    op.create_index('idx_api_key_key', 'api_keys', ['key'])
    op.create_index('idx_api_key_user_id', 'api_keys', ['user_id'])
    op.create_index('idx_api_key_application', 'api_keys', ['application'])
    op.create_index('idx_api_key_active', 'api_keys', ['is_active'])
    op.create_index('idx_api_key_expires', 'api_keys', ['expires_at'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_api_key_expires', 'api_keys')
    op.drop_index('idx_api_key_active', 'api_keys')
    op.drop_index('idx_api_key_application', 'api_keys')
    op.drop_index('idx_api_key_user_id', 'api_keys')
    op.drop_index('idx_api_key_key', 'api_keys')
    
    # Drop the table
    op.drop_table('api_keys')
