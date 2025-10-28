"""add_workspace_id_to_retrospectives

Revision ID: 372c7e4d8e04
Revises: 0004_add_workspace_id
Create Date: 2025-10-27 20:28:00.420483

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '372c7e4d8e04'
down_revision = '0004_add_workspace_id'
branch_labels = None
depends_on = None


def upgrade():
    # Add workspace_id column to retrospectives table (nullable initially)
    op.execute("""
        ALTER TABLE retrospectives 
        ADD COLUMN IF NOT EXISTS workspace_id INTEGER;
    """)
    
    # Add sprint_name column
    op.execute("""
        ALTER TABLE retrospectives 
        ADD COLUMN IF NOT EXISTS sprint_name VARCHAR(100);
    """)
    
    # Add facilitator_id column
    op.execute("""
        ALTER TABLE retrospectives 
        ADD COLUMN IF NOT EXISTS facilitator_id INTEGER REFERENCES users(id);
    """)
    
    # Add created_by column if it doesn't exist
    op.execute("""
        ALTER TABLE retrospectives 
        ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id);
    """)
    
    # Add scheduling columns
    op.execute("""
        ALTER TABLE retrospectives 
        ADD COLUMN IF NOT EXISTS scheduled_start_time TIMESTAMP WITH TIME ZONE,
        ADD COLUMN IF NOT EXISTS scheduled_end_time TIMESTAMP WITH TIME ZONE,
        ADD COLUMN IF NOT EXISTS actual_start_time TIMESTAMP WITH TIME ZONE,
        ADD COLUMN IF NOT EXISTS actual_end_time TIMESTAMP WITH TIME ZONE;
    """)
    
    # Add status and phase columns
    op.execute("""
        ALTER TABLE retrospectives 
        ADD COLUMN IF NOT EXISTS current_phase VARCHAR(20) DEFAULT 'input',
        ADD COLUMN IF NOT EXISTS phase_completion JSONB DEFAULT '{}';
    """)
    
    # Add settings and AI columns
    op.execute("""
        ALTER TABLE retrospectives 
        ADD COLUMN IF NOT EXISTS settings JSONB DEFAULT '{}',
        ADD COLUMN IF NOT EXISTS ai_summary TEXT,
        ADD COLUMN IF NOT EXISTS ai_insights JSONB;
    """)
    
    # Create indexes
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_retrospectives_scheduled_start 
        ON retrospectives(scheduled_start_time);
        
        CREATE INDEX IF NOT EXISTS idx_retrospectives_current_phase 
        ON retrospectives(current_phase);
    """)
    
    # Note: Skip data migration since team_id might be a different type
    
    # Add foreign key constraint if workspaces table exists
    op.execute("""
        DO $$ 
        BEGIN 
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'workspaces') THEN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'retrospectives_workspace_id_fkey'
                ) THEN
                    ALTER TABLE retrospectives 
                    ADD CONSTRAINT retrospectives_workspace_id_fkey 
                    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE;
                END IF;
            END IF;
        END $$;
    """)
    
    # Create index for workspace
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_retrospectives_workspace 
        ON retrospectives(workspace_id);
    """)
    
    # Note: We don't make workspace_id NOT NULL yet because there might be old rows


def downgrade():
    # Drop foreign key constraint
    op.execute("""
        ALTER TABLE retrospectives 
        DROP CONSTRAINT IF EXISTS retrospectives_workspace_id_fkey;
    """)
    
    # Drop index
    op.execute("DROP INDEX IF EXISTS idx_retrospectives_workspace")
    
    # Drop column
    op.execute("""
        ALTER TABLE retrospectives 
        DROP COLUMN IF EXISTS workspace_id;
    """)


