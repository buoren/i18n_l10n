"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-09-25 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create greetings table
    op.create_table('greetings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('greeting_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_id', 'greetings', ['user_id'])
    op.create_index('idx_created_at', 'greetings', ['created_at'])
    
    # Create counters table
    op.create_table('counters',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('counter_value', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_session_id', 'counters', ['session_id'])
    
    # Create translation_tags table
    op.create_table('translation_tags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('application', sa.String(length=255), nullable=False),
        sa.Column('tag', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_application', 'translation_tags', ['application'])
    
    # Create translations table
    op.create_table('translations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('translation_tag_id', sa.Integer(), nullable=False),
        sa.Column('language', mysql.ENUM(
            'en-US', 'en-GB', 'es-ES', 'es-MX', 'fr-FR', 'fr-CA', 'de-DE', 'it-IT',
            'pt-BR', 'pt-PT', 'ru-RU', 'ja-JP', 'ko-KR', 'zh-CN', 'zh-TW', 'ar-SA',
            'hi-IN', 'nl-NL', 'sv-SE', 'no-NO', 'da-DK', 'fi-FI', 'pl-PL', 'cs-CZ',
            'hu-HU', 'ro-RO', 'bg-BG', 'hr-HR', 'sk-SK', 'sl-SI', 'et-EE', 'lv-LV',
            'lt-LT', 'el-GR', 'tr-TR', 'uk-UA', 'th-TH', 'vi-VN', 'id-ID', 'ms-MY',
            'tl-PH'
        ), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('context', sa.String(length=500), nullable=True),
        sa.Column('is_plural', sa.Boolean(), nullable=True),
        sa.Column('plural_form', sa.String(length=50), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('translation_tag_id', 'language', 'plural_form', name='unique_translation')
    )
    op.create_index('idx_translation_tag_id', 'translations', ['translation_tag_id'])
    op.create_index('idx_language', 'translations', ['language'])
    op.create_index('idx_active', 'translations', ['is_active'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('translations')
    op.drop_table('translation_tags')
    op.drop_table('counters')
    op.drop_table('greetings')
    op.drop_table('users')
