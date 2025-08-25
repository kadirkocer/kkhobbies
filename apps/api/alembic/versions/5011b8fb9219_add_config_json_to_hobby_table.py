"""Add config_json to hobby table

Revision ID: 5011b8fb9219
Revises: v2_1_additions
Create Date: 2025-08-25 12:27:43.712165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5011b8fb9219'
down_revision = 'v2_1_additions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add config_json column to hobby table
    op.add_column('hobby', sa.Column('config_json', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove config_json column from hobby table
    op.drop_column('hobby', 'config_json')