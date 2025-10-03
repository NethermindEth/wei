"""
Migration script to add content column to analyses table.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Add content column to analyses table."""
    op.add_column('analyses', sa.Column('content', sa.Text(), nullable=True))

def downgrade():
    """Remove content column from analyses table."""
    op.drop_column('analyses', 'content')
