"""add_code_to_retrospectives

Revision ID: bcb50145deeb
Revises: db0a6db0d497
Create Date: 2025-10-31 09:12:28.978070

"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'bcb50145deeb'
down_revision = 'db0a6db0d497'
branch_labels = None
depends_on = None


def upgrade():
    # Add code column to retrospectives table
    op.add_column('retrospectives', sa.Column('code', sa.String(length=5), nullable=True))
    
    # Generate codes for existing retrospectives
    import string
    import secrets
    
    connection = op.get_bind()
    
    # Get all retrospectives without codes
    result = connection.execute(sa.text("SELECT id FROM retrospectives WHERE code IS NULL"))
    retro_ids = [row[0] for row in result]
    
    # Generate unique codes
    alphabet = string.ascii_uppercase + string.digits
    # Exclude similar-looking characters
    alphabet = ''.join(c for c in alphabet if c not in '0O1IL')
    
    for retro_id in retro_ids:
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(5))
            # Check if code already exists
            existing = connection.execute(
                sa.text("SELECT id FROM retrospectives WHERE code = :code"),
                {'code': code}
            ).fetchone()
            if not existing:
                connection.execute(
                    sa.text("UPDATE retrospectives SET code = :code WHERE id = :retro_id"),
                    {'code': code, 'retro_id': retro_id}
                )
                break
    
    # Now make code NOT NULL and add unique constraint
    op.alter_column('retrospectives', 'code', nullable=False)
    op.create_index('ix_retrospectives_code', 'retrospectives', ['code'], unique=True)


def downgrade():
    # Remove unique index
    op.drop_index('ix_retrospectives_code', 'retrospectives')
    
    # Remove code column
    op.drop_column('retrospectives', 'code')


