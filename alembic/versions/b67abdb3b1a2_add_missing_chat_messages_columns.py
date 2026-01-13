"""add_missing_chat_messages_columns

Revision ID: b67abdb3b1a2
Revises: a03c5f94b7ba
Create Date: 2025-10-27 21:23:22.803595

"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'b67abdb3b1a2'
down_revision = 'a03c5f94b7ba'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to chat_messages
    op.execute("""
        ALTER TABLE chat_messages 
        ADD COLUMN IF NOT EXISTS current_category VARCHAR(20),
        ADD COLUMN IF NOT EXISTS metadata JSONB;
    """)


def downgrade():
    # Drop columns from chat_messages
    op.execute("""
        ALTER TABLE chat_messages 
        DROP COLUMN IF EXISTS current_category,
        DROP COLUMN IF EXISTS metadata;
    """)


