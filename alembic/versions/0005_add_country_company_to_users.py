"""Add country_name and company_name to users table

Revision ID: 0005_country_company
Revises: db0a6db0d497
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0005_country_company'
down_revision = 'db0a6db0d497'
branch_labels = None
depends_on = None


def upgrade():
    # Add country_name and company_name columns to users table (PostgreSQL-safe)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'country_name'
            ) THEN
                ALTER TABLE users ADD COLUMN country_name VARCHAR(100);
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'company_name'
            ) THEN
                ALTER TABLE users ADD COLUMN company_name VARCHAR(255);
            END IF;
        END $$;
    """)
    
    # Set default values for existing users
    op.execute("""
        UPDATE users 
        SET country_name = 'Kenya', 
            company_name = 'Taistat'
        WHERE country_name IS NULL OR company_name IS NULL;
    """)


def downgrade():
    # Remove added columns
    op.execute("""
        ALTER TABLE users 
        DROP COLUMN IF EXISTS country_name,
        DROP COLUMN IF EXISTS company_name;
    """)
