"""make_action_items_retrospective_and_workspace_nullable

Revision ID: c6f0ca6ec5cb
Revises: bcb50145deeb
Create Date: 2025-10-31 09:57:32.984155

"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'c6f0ca6ec5cb'
down_revision = 'bcb50145deeb'
branch_labels = None
depends_on = None


def upgrade():
    # Make retrospective_id and workspace_id nullable in action_items table
    op.alter_column('action_items', 'retrospective_id', nullable=True)
    op.alter_column('action_items', 'workspace_id', nullable=True)


def downgrade():
    # Make them non-nullable again
    op.alter_column('action_items', 'retrospective_id', nullable=False)
    op.alter_column('action_items', 'workspace_id', nullable=False)


