"""create workspace_invitations table

Revision ID: 0004_create_workspace_invitations
Revises: 0003_add_user_columns
Create Date: 2025-10-30 00:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004_create_workspace_invitations'
down_revision = '0003_add_user_columns'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'workspace_invitations',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('workspace_id', sa.Integer(), sa.ForeignKey('workspaces.id'), nullable=False),
        sa.Column('invited_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=True),
        sa.Column('token', sa.String(255), nullable=False, unique=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('declined_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Indexes
    op.create_index('ix_workspace_invitations_id', 'workspace_invitations', ['id'], unique=False)
    op.create_index('ix_workspace_invitations_token', 'workspace_invitations', ['token'], unique=True)


def downgrade():
    op.drop_index('ix_workspace_invitations_token', table_name='workspace_invitations')
    op.drop_index('ix_workspace_invitations_id', table_name='workspace_invitations')
    op.drop_table('workspace_invitations')


