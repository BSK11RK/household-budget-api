from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ExpenseModel, IncomeModel, UserModel, BudgetModel
from app.schemas import (
    CategoryExpenseTotal,
    MonthlyCategoryReport,
    MonthlyReport,
    MonthlyOverviewReport
)
from app.security import get_current_user


router = APIRouter(prefix="/reports", tags=["Reports"])


# 月次収支レポート
@router.get("/monthly", response_model=MonthlyReport)
def get_monthly_report(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 集計対象の月の開始日と翌月の開始日
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    # その月の収入合計
    income_statement = select(
        func.coalesce(func.sum(IncomeModel.amount), 0)
    ).where(
        IncomeModel.user_id == current_user.id,
        IncomeModel.income_date >= start_date,
        IncomeModel.income_date < end_date
    )

    income_total = db.scalar(income_statement) or 0

    # その月の支出合計
    expense_statement = select(
        func.coalesce(func.sum(ExpenseModel.amount), 0)
    ).where(
        ExpenseModel.user_id == current_user.id,
        ExpenseModel.expense_date >= start_date,
        ExpenseModel.expense_date < end_date
    )

    expense_total = db.scalar(expense_statement) or 0

    # 収支を計算
    balance = income_total - expense_total

    return MonthlyReport(
        year=year,
        month=month,
        income_total=income_total,
        expense_total=expense_total,
        balance=balance
    )


# 月次カテゴリ別支出レポート
@router.get(
    "/monthly/categories",
    response_model=MonthlyCategoryReport
)
def get_monthly_category_report(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 集計対象の月の開始日と翌月の開始日
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    # カテゴリごとに支出金額を合計
    statement = (
        select(
            ExpenseModel.category,
            func.sum(ExpenseModel.amount).label("total"),
        )
        .where(
            ExpenseModel.user_id == current_user.id,
            ExpenseModel.expense_date >= start_date,
            ExpenseModel.expense_date < end_date
        )
        .group_by(ExpenseModel.category)
        .order_by(func.sum(ExpenseModel.amount).desc())
    )

    rows = db.execute(statement).all()

    # 集計結果をレスポンス用の形式に変換
    categories = [
        CategoryExpenseTotal(
            category=row.category,
            total=row.total
        )
        for row in rows
    ]

    return MonthlyCategoryReport(
        year=year,
        month=month,
        categories=categories
    )
    
    
@router.get("/overview", response_model=MonthlyOverviewReport)
def get_monthly_overview(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 集計対象の月を決める
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    # 収入の合計
    income_statement = select(
        func.coalesce(func.sum(IncomeModel.amount), 0)
    ).where(
        IncomeModel.user_id == current_user.id,
        IncomeModel.income_date >= start_date,
        IncomeModel.income_date < end_date
    )
    income_total = db.scalar(income_statement) or 0

    # 支出の合計
    expense_statement = select(
        func.coalesce(func.sum(ExpenseModel.amount), 0)
    ).where(
        ExpenseModel.user_id == current_user.id,
        ExpenseModel.expense_date >= start_date,
        ExpenseModel.expense_date < end_date
    )
    expense_total = db.scalar(expense_statement) or 0

    # その月の予算を取得
    budget_statement = select(BudgetModel).where(
        BudgetModel.user_id == current_user.id,
        BudgetModel.year == year,
        BudgetModel.month == month
    )
    budgets = db.scalars(budget_statement).all()

    budget_total = sum(budget.amount for budget in budgets)

    # 予算を超えたカテゴリを調べる
    categories_over_budget = []

    for budget in budgets:
        category_expense_statement = select(
            func.coalesce(func.sum(ExpenseModel.amount), 0)
        ).where(
            ExpenseModel.user_id == current_user.id,
            ExpenseModel.category == budget.category,
            ExpenseModel.expense_date >= start_date,
            ExpenseModel.expense_date < end_date
        )

        category_spent = (
            db.scalar(category_expense_statement) or 0
        )

        if category_spent > budget.amount:
            categories_over_budget.append(budget.category)

    return MonthlyOverviewReport(
        year=year,
        month=month,
        income_total=income_total,
        expense_total=expense_total,
        balance=income_total - expense_total,
        budget_total=budget_total,
        budget_remaining=budget_total - expense_total,
        categories_over_budget=categories_over_budget
    )