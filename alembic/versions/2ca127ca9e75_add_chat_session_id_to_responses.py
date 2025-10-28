"""add_chat_session_id_to_responses

Revision ID: 2ca127ca9e75
Revises: b67abdb3b1a2
Create Date: 2025-10-27 21:31:30.512091

"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '2ca127ca9e75'
down_revision = 'b67abdb3b1a2'
branch_labels = None
depends_on = None


def upgrade():
    # Add chat_session_id column to retrospective_responses
    op.execute("""
        ALTER TABLE retrospective_responses 
        ADD COLUMN IF NOT EXISTS chat_session_id INTEGER REFERENCES chat_sessions(id);
    """)


def downgrade():
    # Drop chat_session_id column from retrospective_responses
    op.execute("""
        ALTER TABLE retrospective_responses 
        DROP COLUMN IF EXISTS chat_session_id;
    """)


