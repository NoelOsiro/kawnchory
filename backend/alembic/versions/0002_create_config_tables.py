"""create additional config tables

Revision ID: 0002_create_config_tables
Revises: 0001_create_segmentor_configs
Create Date: 2025-11-21 00:01:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_create_config_tables'
down_revision = '0001_create_segmentor_configs'
branch_labels = None
depends_on = None


def upgrade():
    # node_configs
    op.create_table(
        'node_configs',
        sa.Column('name', sa.String(), primary_key=True, nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )

    # routing_rules
    op.create_table(
        'routing_rules',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('source_node', sa.String(), nullable=False),
        sa.Column('condition', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('target_node', sa.String(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )

    # rag_retrieval_configs
    op.create_table(
        'rag_retrieval_configs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('index_name', sa.String(length=200), nullable=True),
        sa.Column('vector_db', sa.String(length=100), nullable=True),
        sa.Column('top_k', sa.Integer(), nullable=False, server_default=sa.text('5')),
        sa.Column('filters', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('rerank', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('rerank_model', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )

    # offers_configs
    op.create_table(
        'offers_configs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('model_name', sa.String(length=200), nullable=True),
        sa.Column('max_offers', sa.Integer(), nullable=True),
        sa.Column('personalization', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )

    # safety_configs
    op.create_table(
        'safety_configs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('toxicity_threshold', sa.Float(), nullable=False, server_default=sa.text('0.7')),
        sa.Column('hallucination_check', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('banned_keywords', sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )

    # generation_configs
    op.create_table(
        'generation_configs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('model_name', sa.String(length=200), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=False, server_default=sa.text('0.7')),
        sa.Column('max_tokens', sa.Integer(), nullable=False, server_default=sa.text('512')),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )

    # delivery_configs
    op.create_table(
        'delivery_configs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=True),
        sa.Column('format', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )


def downgrade():
    op.drop_table('delivery_configs')
    op.drop_table('generation_configs')
    op.drop_table('safety_configs')
    op.drop_table('offers_configs')
    op.drop_table('rag_retrieval_configs')
    op.drop_table('routing_rules')
    op.drop_table('node_configs')
