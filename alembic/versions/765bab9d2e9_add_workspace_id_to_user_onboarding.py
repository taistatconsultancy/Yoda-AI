"""add_workspace_id_to_user_onboarding

Revision ID: 765bab9d2e9
Revises: db62da066f3b
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '765bab9d2e9'
down_revision = 'db62da066f3b'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Drop the existing unique constraint on user_id
    op.execute("""
        ALTER TABLE user_onboarding 
        DROP CONSTRAINT IF EXISTS user_onboarding_user_id_key;
    """)
    
    # Step 2: Add workspace_id column (nullable initially for data migration)
    op.execute("""
        ALTER TABLE user_onboarding 
        ADD COLUMN IF NOT EXISTS workspace_id INTEGER;
    """)
    
    # Step 3: For existing records, try to assign them to the user's first workspace
    # This handles the migration of existing data
    op.execute("""
        UPDATE user_onboarding uo
        SET workspace_id = (
            SELECT w.id 
            FROM workspaces w 
            WHERE w.created_by = uo.user_id 
            ORDER BY w.id 
            LIMIT 1
        )
        WHERE uo.workspace_id IS NULL;
    """)
    
    # Step 4: Delete any records that couldn't be assigned to a workspace
    # (users with no workspaces - these are orphaned onboarding records)
    op.execute("""
        DELETE FROM user_onboarding 
        WHERE workspace_id IS NULL;
    """)
    
    # Step 5: Now make workspace_id NOT NULL since all records should have one
    op.execute("""
        ALTER TABLE user_onboarding 
        ALTER COLUMN workspace_id SET NOT NULL;
    """)
    
    # Step 6: Add foreign key constraint
    op.execute("""
        DO $$ 
        BEGIN 
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'workspaces') THEN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'user_onboarding_workspace_id_fkey'
                ) THEN
                    ALTER TABLE user_onboarding 
                    ADD CONSTRAINT user_onboarding_workspace_id_fkey 
                    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE;
                END IF;
            END IF;
        END $$;
    """)
    
    # Step 7: Create composite unique constraint on (user_id, workspace_id)
    op.execute("""
        ALTER TABLE user_onboarding 
        ADD CONSTRAINT uq_user_workspace_onboarding 
        UNIQUE (user_id, workspace_id);
    """)
    
    # Step 8: Create index for workspace_id for better query performance
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_onboarding_workspace 
        ON user_onboarding(workspace_id);
    """)


def downgrade():
    # Drop the composite unique constraint
    op.execute("""
        ALTER TABLE user_onboarding 
        DROP CONSTRAINT IF EXISTS uq_user_workspace_onboarding;
    """)
    
    # Drop the index
    op.execute("""
        DROP INDEX IF EXISTS idx_user_onboarding_workspace;
    """)
    
    # Drop foreign key constraint
    op.execute("""
        ALTER TABLE user_onboarding 
        DROP CONSTRAINT IF EXISTS user_onboarding_workspace_id_fkey;
    """)
    
    # Drop workspace_id column
    op.execute("""
        ALTER TABLE user_onboarding 
        DROP COLUMN IF EXISTS workspace_id;
    """)
    
    # Restore the original unique constraint on user_id
    op.execute("""
        ALTER TABLE user_onboarding 
        ADD CONSTRAINT user_onboarding_user_id_key UNIQUE (user_id);
    """)

