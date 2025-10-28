"""Add workspace_id to action_items

Revision ID: 0004
Revises: 0003
Create Date: 2025-10-27
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004_add_workspace_id'
down_revision = '0003_add_user_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Add workspace_id column to action_items if it doesn't exist
    op.execute("""
        ALTER TABLE action_items 
        ADD COLUMN IF NOT EXISTS workspace_id INTEGER,
        ADD COLUMN IF NOT EXISTS discussion_topic_id INTEGER;
    """)
    
    # Add foreign key constraints
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'action_items_workspace_id_fkey'
            ) THEN
                ALTER TABLE action_items 
                ADD CONSTRAINT action_items_workspace_id_fkey 
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'action_items_discussion_topic_id_fkey'
            ) THEN
                ALTER TABLE action_items 
                ADD CONSTRAINT action_items_discussion_topic_id_fkey 
                FOREIGN KEY (discussion_topic_id) REFERENCES discussion_topics(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)
    
    # Create index
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_action_items_workspace 
        ON action_items(workspace_id);
    """)


def downgrade():
    # Drop foreign keys
    op.execute("""
        ALTER TABLE action_items 
        DROP CONSTRAINT IF EXISTS action_items_workspace_id_fkey,
        DROP CONSTRAINT IF EXISTS action_items_discussion_topic_id_fkey;
    """)
    
    # Drop columns
    op.execute("""
        ALTER TABLE action_items 
        DROP COLUMN IF EXISTS workspace_id,
        DROP COLUMN IF EXISTS discussion_topic_id;
    """)
    
    # Drop index
    op.execute("DROP INDEX IF EXISTS idx_action_items_workspace")
