"""取引日に関するカラムを追加

Revision ID: 124f8ebd48b7
Revises: 73bc94218bfd
Create Date: 2026-10-17 20:35:11.787241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '124f8ebd48b7'
down_revision: Union[str, Sequence[str], None] = '73bc94218bfd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    with op.batch_alter_table("expenses") as batch_op:
        batch_op.add_column(
            sa.Column("expense_date", sa.Date(), nullable=True)
        )

    with op.batch_alter_table("incomes") as batch_op:
        batch_op.add_column(
            sa.Column("income_date", sa.Date(), nullable=True)
        )

    op.execute(
        sa.text(
            "UPDATE expenses "
            "SET expense_date = date(created_at) "
            "WHERE expense_date IS NULL"
        )
    )

    op.execute(
        sa.text(
            "UPDATE incomes "
            "SET income_date = date(created_at) "
            "WHERE income_date IS NULL"
        )
    )


    with op.batch_alter_table("expenses") as batch_op:
        batch_op.alter_column(
            "expense_date",
            existing_type=sa.Date(),
            nullable=False
        )
        batch_op.create_index(
            "ix_expenses_expense_date",
            ["expense_date"],
            unique=False
        )

    with op.batch_alter_table("incomes") as batch_op:
        batch_op.alter_column(
            "income_date",
            existing_type=sa.Date(),
            nullable=False
        )
        batch_op.create_index(
            "ix_incomes_income_date",
            ["income_date"],
            unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("incomes") as batch_op:
        batch_op.drop_index("ix_incomes_income_date")
        batch_op.drop_column("income_date")

    with op.batch_alter_table("expenses") as batch_op:
        batch_op.drop_index("ix_expenses_expense_date")
        batch_op.drop_column("expense_date")