"""initial tables

Revision ID: 0001_initial
Revises: 
Create Date: 2025-10-10 00:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('provider_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table(
        'retrospectives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sprint_id', sa.String(), nullable=True),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_retrospectives_id'), 'retrospectives', ['id'], unique=False)

    op.create_table(
        'sprint_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sprint_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('team_size', sa.Integer(), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.Column('processed_data', sa.JSON(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('processing_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sprint_summaries_id'), 'sprint_summaries', ['id'], unique=False)
    op.create_index(op.f('ix_sprint_summaries_sprint_id'), 'sprint_summaries', ['sprint_id'], unique=True)

    op.create_table(
        'retrospective_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('retrospective_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('liked', sa.Text(), nullable=True),
        sa.Column('learned', sa.Text(), nullable=True),
        sa.Column('lacked', sa.Text(), nullable=True),
        sa.Column('longed_for', sa.Text(), nullable=True),
        sa.Column('sentiment_score', sa.Integer(), nullable=True),
        sa.Column('sentiment_label', sa.String(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('follow_up_questions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['retrospective_id'], ['retrospectives.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_retrospective_responses_id'), 'retrospective_responses', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_retrospective_responses_id'), table_name='retrospective_responses')
    op.drop_table('retrospective_responses')
    op.drop_index(op.f('ix_sprint_summaries_sprint_id'), table_name='sprint_summaries')
    op.drop_index(op.f('ix_sprint_summaries_id'), table_name='sprint_summaries')
    op.drop_table('sprint_summaries')
    op.drop_index(op.f('ix_retrospectives_id'), table_name='retrospectives')
    op.drop_table('retrospectives')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')


