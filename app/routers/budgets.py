from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BudgetModel, ExpenseModel, UserModel
from app.schemas import (
    BudgetCategoryResult,
    BudgetCreate,
    BudgetResponse,
    MonthlyBudgetReport
)
from app.security import get_current_user


router = APIRouter(prefix="/budgets", tags=["Budgets"])


# POST
@router.post(
    "",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED
)
def create_budget(
    data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    statement = select(BudgetModel).where(
        BudgetModel.user_id == current_user.id,
        BudgetModel.year == data.year,
        BudgetModel.month == data.month,
        BudgetModel.category == data.category
    )

    existing_budget = db.scalar(statement)

    if existing_budget is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="この月・カテゴリの予算はすでに登録されています"
        )

    budget = BudgetModel(**data.model_dump(), user_id=current_user.id)

    db.add(budget)
    db.commit()
    db.refresh(budget)

    return budget


# GET
@router.get("/monthly", response_model=MonthlyBudgetReport)
def get_monthly_budget_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 年月の入力を検証する
    if not 2000 <= year <= 2100:
        raise HTTPException(
            status_code=422,
            detail="yearは2000から2100の範囲で指定してください"
        )

    if not 1 <= month <= 12:
        raise HTTPException(
            status_code=422,
            detail="monthは1から12の範囲で指定してください"
        )

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    budget_statement = (
        select(BudgetModel)
        .where(
            BudgetModel.user_id == current_user.id,
            BudgetModel.year == year,
            BudgetModel.month == month
        )
        .order_by(BudgetModel.category)
    )

    budgets = db.scalars(budget_statement).all()

    results = []

    for budget in budgets:
        expense_statement = select(
            func.coalesce(func.sum(ExpenseModel.amount), 0)
        ).where(
            ExpenseModel.user_id == current_user.id,
            ExpenseModel.category == budget.category,
            ExpenseModel.expense_date >= start_date,
            ExpenseModel.expense_date < end_date
        )

        spent_amount = db.scalar(expense_statement) or 0

        remaining_amount = budget.amount - spent_amount

        if budget.amount == 0:
            usage_rate = 0.0 if spent_amount == 0 else 100.0
        else:
            usage_rate = round(
                spent_amount / budget.amount * 100,
                1
            )

        results.append(
            BudgetCategoryResult(
                category=budget.category,
                budget_amount=budget.amount,
                spent_amount=spent_amount,
                remaining_amount=remaining_amount,
                usage_rate=usage_rate
            )
        )

    return MonthlyBudgetReport(
        year=year,
        month=month,
        categories=results
    )