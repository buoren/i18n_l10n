"""Move context from Translation to TranslationTag

Revision ID: 0003
Revises: 0002
Create Date: 2025-09-25 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add context column to translation_tags table
    op.add_column('translation_tags', sa.Column('context', sa.String(length=500), nullable=True))
    
    # Migrate existing context data from translations to translation_tags
    # This is a data migration - we'll copy context from the first translation of each tag
    op.execute("""
        UPDATE translation_tags tt
        SET context = (
            SELECT t.context 
            FROM translations t 
            WHERE t.translation_tag_id = tt.id 
            AND t.context IS NOT NULL 
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM translations t 
            WHERE t.translation_tag_id = tt.id 
            AND t.context IS NOT NULL
        )
    """)
    
    # Remove context column from translations table
    op.drop_column('translations', 'context')


def downgrade() -> None:
    # Add context column back to translations table
    op.add_column('translations', sa.Column('context', sa.String(length=500), nullable=True))
    
    # Migrate context data back from translation_tags to translations
    op.execute("""
        UPDATE translations t
        SET context = (
            SELECT tt.context 
            FROM translation_tags tt 
            WHERE tt.id = t.translation_tag_id 
            AND tt.context IS NOT NULL
        )
        WHERE EXISTS (
            SELECT 1 FROM translation_tags tt 
            WHERE tt.id = t.translation_tag_id 
            AND tt.context IS NOT NULL
        )
    """)
    
    # Remove context column from translation_tags table
    op.drop_column('translation_tags', 'context')
