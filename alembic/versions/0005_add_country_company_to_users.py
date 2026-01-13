"""Add country_name and company_name to users table

Revision ID: 0005_add_country_company_to_users
Revises: db0a6db0d497
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0005_add_country_company_to_users'
down_revision = 'db0a6db0d497'
branch_labels = None
depends_on = None


def upgrade():
    # Add country_name and company_name columns to users table
    op.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS country_name VARCHAR(100),
        ADD COLUMN IF NOT EXISTS company_name VARCHAR(255);
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
