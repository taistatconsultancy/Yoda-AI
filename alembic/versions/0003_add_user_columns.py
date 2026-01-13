"""Add missing user columns

Revision ID: 0003_add_user_columns
Revises: 0002_add_new_models
Create Date: 2025-10-27 13:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003_add_user_columns'
down_revision = '0002_add_new_models'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to users table if they don't exist
    op.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE,
        ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE,
        ADD COLUMN IF NOT EXISTS profile_picture_url TEXT,
        ADD COLUMN IF NOT EXISTS default_role VARCHAR(20) DEFAULT 'member',
        ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC',
        ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{"email": true, "in_app": true}'::jsonb,
        ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;
    """)
    
    # Rename password to hashed_password if needed
    op.execute("""
        DO $$ 
        BEGIN 
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='users' AND column_name='password') THEN
                ALTER TABLE users RENAME COLUMN password TO hashed_password;
            END IF;
        END $$;
    """)
    
    # Make full_name NOT NULL if it isn't already
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN full_name SET NOT NULL;
    """)
    
    # Add indexes if they don't exist
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_users_email_verified ON users(email_verified);
        CREATE INDEX IF NOT EXISTS ix_users_google_id ON users(google_id);
    """)
    
    # Remove old columns if they exist
    op.execute("""
        ALTER TABLE users 
        DROP COLUMN IF EXISTS is_verified,
        DROP COLUMN IF EXISTS provider_id,
        DROP COLUMN IF EXISTS provider;
    """)


def downgrade():
    # Remove added columns
    op.execute("""
        ALTER TABLE users 
        DROP COLUMN IF EXISTS email_verified,
        DROP COLUMN IF EXISTS email_verified_at,
        DROP COLUMN IF EXISTS google_id,
        DROP COLUMN IF EXISTS profile_picture_url,
        DROP COLUMN IF EXISTS default_role,
        DROP COLUMN IF EXISTS timezone,
        DROP COLUMN IF EXISTS notification_preferences,
        DROP COLUMN IF EXISTS last_login_at;
    """)
    
    # Rename back if needed
    op.execute("""
        DO $$ 
        BEGIN 
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='users' AND column_name='hashed_password') THEN
                ALTER TABLE users RENAME COLUMN hashed_password TO password;
            END IF;
        END $$;
    """)
    
    # Drop indexes if they exist
    op.execute("""
        DROP INDEX IF EXISTS ix_users_email_verified;
        DROP INDEX IF EXISTS ix_users_google_id;
    """)
