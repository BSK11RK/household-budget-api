from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ExpenseModel, IncomeModel, UserModel
from app.schemas import (
    MonthlyReport, 
    MonthlyCategoryReport, 
    CategoryExpenseTotal
)
from app.security import get_current_user


router = APIRouter(prefix="/reports", tags=["Reports"])


# Monthly_Get
@router.get("/monthly", response_model=MonthlyReport)
def get_monthly_report(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 集計対象の月の開始日時と、翌月の開始日時を求める
    start_date = datetime(year, month, 1)

    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    # その月の収入を合計（データがなければ0）
    income_statement = select(
        func.coalesce(func.sum(IncomeModel.amount), 0)
    ).where(
        IncomeModel.user_id == current_user.id,
        IncomeModel.created_at >= start_date,
        IncomeModel.created_at < end_date
    )
    income_total = db.scalar(income_statement)

    # その月の支出を合計（データがなければ0）
    expense_statement = select(
        func.coalesce(func.sum(ExpenseModel.amount), 0)
    ).where(
        ExpenseModel.user_id == current_user.id,
        ExpenseModel.created_at >= start_date,
        ExpenseModel.created_at < end_date
    )
    expense_total = db.scalar(expense_statement)

    # 収支を計算
    balance = income_total - expense_total

    return MonthlyReport(
        year=year,
        month=month,
        income_total=income_total,
        expense_total=expense_total,
        balance=balance
    )
    
    
# Monthly_Categories_Get
@router.get("/monthly/categories", response_model=MonthlyCategoryReport)
def get_monthly_category_report(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 集計する月の開始日時と翌月の開始日時
    start_data = datetime(year, month, 1)
    
    if month == 12:
        end_data = datetime(year + 1, 1, 1)
    else:
        end_data = datetime(year, month + 1, 1)
        
    # カテゴリごとに支出金額を合計
    statement = (
        select(
            ExpenseModel.category,
            func.sum(ExpenseModel.amount).label("total")
        )
        .where(
            ExpenseModel.user_id == current_user.id,
            ExpenseModel.created_at >= start_data,
            ExpenseModel.created_at < end_data
        )
        .group_by(ExpenseModel.category)
        .order_by(func.sum(ExpenseModel.amount).desc())
    )
    
    rows = db.execute(statement).all()
    
    # 集計結果をレスポンス用の形式にする
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