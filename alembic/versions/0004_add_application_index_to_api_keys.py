"""Add index to application column in api_keys table

Revision ID: 0004
Revises: 0003
Create Date: 2025-09-25 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add index to application column in api_keys table
    op.create_index('ix_api_keys_application', 'api_keys', ['application'])


def downgrade() -> None:
    # Remove index from application column
    op.drop_index('ix_api_keys_application', table_name='api_keys')
