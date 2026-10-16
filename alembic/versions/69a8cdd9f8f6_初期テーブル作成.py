"""初期テーブル作成

Revision ID: 69a8cdd9f8f6
Revises: 
Create Date: 2026-10-16 16:25:40.753591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '69a8cdd9f8f6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass