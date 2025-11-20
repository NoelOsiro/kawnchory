"""create segmentor_configs table

Revision ID: 0001_create_segmentor_configs
Revises: 
Create Date: 2025-11-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_segmentor_configs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'segmentor_configs',
        sa.Column('segmentor_name', sa.String(), primary_key=True, nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True),
    )


def downgrade():
    op.drop_table('segmentor_configs')
