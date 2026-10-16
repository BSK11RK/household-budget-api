
"""作成日時と更新日時を追加

Revision ID: 61b1a46b824a
Revises: 69a8cdd9f8f6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "61b1a46b824a"
down_revision: Union[str, Sequence[str], None] = "69a8cdd9f8f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 既存テーブルに、まずNULLを許可してカラムを追加する
    for table_name in ("expenses", "users"):
        op.add_column(
            table_name,
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=True
            )
        )

        op.add_column(
            table_name,
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=True
            )
        )

        # 既存レコードにも現在の日時を設定する
        op.execute(
            sa.text(
                f"""
                UPDATE {table_name}
                SET created_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL
                """
            )
        )

        op.execute(
            sa.text(
                f"""
                UPDATE {table_name}
                SET updated_at = CURRENT_TIMESTAMP
                WHERE updated_at IS NULL
                """
            )
        )

        # 既存データを埋めてから、NOT NULLとデフォルト値を設定する
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.alter_column(
                "created_at",
                existing_type=sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP")
            )

            batch_op.alter_column(
                "updated_at",
                existing_type=sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP")
            )


def downgrade() -> None:
    # 追加したカラムを削除する
    for table_name in ("users", "expenses"):
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_column("updated_at")
            batch_op.drop_column("created_at")