
"""ユーザーに更新日時を追加

Revision ID: 8feeede79384
Revises: 61b1a46b824a
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8feeede79384"
down_revision: Union[str, Sequence[str], None] = "61b1a46b824a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        )
    )


def downgrade() -> None:
    op.drop_column("users", "updated_at")