"""fix_chat_sessions_schema

Revision ID: a03c5f94b7ba
Revises: 372c7e4d8e04
Create Date: 2025-10-27 21:03:22.851781

"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'a03c5f94b7ba'
down_revision = '372c7e4d8e04'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to chat_sessions
    op.execute("""
        ALTER TABLE chat_sessions 
        ADD COLUMN IF NOT EXISTS current_category VARCHAR(20) DEFAULT 'liked',
        ADD COLUMN IF NOT EXISTS categories_completed JSONB DEFAULT '{"liked": false, "learned": false, "lacked": false, "longed_for": false}',
        ADD COLUMN IF NOT EXISTS is_completed BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE,
        ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    """)
    
    # Add missing columns to chat_messages
    op.execute("""
        ALTER TABLE chat_messages 
        ADD COLUMN IF NOT EXISTS metadata JSONB,
        ADD COLUMN IF NOT EXISTS ai_tokens_used INTEGER;
    """)
    
    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_category ON chat_sessions(current_category);")


def downgrade():
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_chat_sessions_category")
    
    # Drop columns from chat_messages
    op.execute("""
        ALTER TABLE chat_messages 
        DROP COLUMN IF EXISTS metadata,
        DROP COLUMN IF EXISTS ai_tokens_used;
    """)
    
    # Drop columns from chat_sessions
    op.execute("""
        ALTER TABLE chat_sessions 
        DROP COLUMN IF EXISTS current_category,
        DROP COLUMN IF EXISTS categories_completed,
        DROP COLUMN IF EXISTS is_completed,
        DROP COLUMN IF EXISTS started_at,
        DROP COLUMN IF EXISTS completed_at,
        DROP COLUMN IF EXISTS last_activity_at;
    """)


