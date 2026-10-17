from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ExpenseModel, UserModel
from app.schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    MonthlySummary,
    CategorySummaryItem,
    MonthlyTrendItem
)
from app.security import get_current_user


router = APIRouter(prefix="/expenses", tags=["Expenses"])


# GET
@router.get("", response_model=list[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    statement = (
        select(ExpenseModel)
        .where(ExpenseModel.user_id == current_user.id)
        .order_by(ExpenseModel.expense_date.desc())
    )

    return db.scalars(statement).all()


# 月別の支出合計
@router.get("/summary/monthly", response_model=MonthlySummary)
def get_monthly_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    statement = select(
        func.sum(ExpenseModel.amount)
    ).where(
        ExpenseModel.user_id == current_user.id,
        ExpenseModel.expense_date >= start_date,
        ExpenseModel.expense_date < end_date
    )

    total = db.scalar(statement)

    return {
        "year": year,
        "month": month,
        "total": total or 0
    }


# カテゴリ別の支出合計
@router.get(
    "/summary/categories",
    response_model=list[CategorySummaryItem]
)
def get_category_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    statement = (
        select(
            ExpenseModel.category,
            func.sum(ExpenseModel.amount).label("total")
        )
        .where(
            ExpenseModel.user_id == current_user.id,
            ExpenseModel.expense_date >= start_date,
            ExpenseModel.expense_date < end_date
        )
        .group_by(ExpenseModel.category)
        .order_by(ExpenseModel.category)
    )

    rows = db.execute(statement).all()

    return [
        {"category": row.category, "total": row.total}
        for row in rows
    ]


# 月ごとの支出推移
@router.get("/summary/monthly-trend", response_model=list[MonthlyTrendItem])
def get_monthly_trend(
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    start_date = date(year, 1, 1)
    end_date = date(year + 1, 1, 1)

    month_expression = extract(
        "month",
        ExpenseModel.expense_date
    )

    statement = (
        select(
            month_expression.label("month"),
            func.sum(ExpenseModel.amount).label("total")
        )
        .where(
            ExpenseModel.user_id == current_user.id,
            ExpenseModel.expense_date >= start_date,
            ExpenseModel.expense_date < end_date
        )
        .group_by(month_expression)
        .order_by(month_expression)
    )

    rows = db.execute(statement).all()

    totals_by_month = {
        int(row.month): int(row.total or 0)
        for row in rows
    }

    # 支出がない月も0円として返す
    return [
        {
            "month": month,
            "total": totals_by_month.get(month, 0)
        }
        for month in range(1, 13)
    ]


# GET_ID
@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    statement = select(ExpenseModel).where(
        ExpenseModel.id == expense_id,
        ExpenseModel.user_id == current_user.id
    )

    expense = db.scalar(statement)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支出が見つかりません"
        )

    return expense


# POST
@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    expense = ExpenseModel(**data.model_dump(), user_id=current_user.id)

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


# PATCH
@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    statement = select(ExpenseModel).where(
        ExpenseModel.id == expense_id,
        ExpenseModel.user_id == current_user.id
    )

    expense = db.scalar(statement)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支出が見つかりません"
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="更新する項目を指定してください"
        )

    for key, value in update_data.items():
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="項目を空にすることはできません"
            )

        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)

    return expense


# DELETE
@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    statement = select(ExpenseModel).where(
        ExpenseModel.id == expense_id,
        ExpenseModel.user_id == current_user.id
    )

    expense = db.scalar(statement)

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="支出が見つかりません"
        )

    db.delete(expense)
    db.commit()