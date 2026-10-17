"""収入テーブルを追加

Revision ID: 73bc94218bfd
Revises: 61b1a46b824a
Create Date: 2026-10-17 11:45:44.991417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '73bc94218bfd'
down_revision: Union[str, Sequence[str], None] = '61b1a46b824a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('incomes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('source', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incomes_id'), 'incomes', ['id'], unique=False)
    op.create_index(op.f('ix_incomes_user_id'), 'incomes', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incomes_user_id'), table_name='incomes')
    op.drop_index(op.f('ix_incomes_id'), table_name='incomes')
    op.drop_table('incomes')