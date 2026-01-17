"""merge country/company columns branch with onboarding/workspace branch

Revision ID: 0006_merge_heads
Revises: 0005_country_company, 765bab9d2e9
Create Date: 2026-01-14

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0006_merge_heads"
down_revision = ("0005_country_company", "765bab9d2e9")
branch_labels = None
depends_on = None


def upgrade():
    # Merge migration (no-op)
    pass


def downgrade():
    # Merge migration (no-op)
    pass

