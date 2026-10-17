from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import IncomeModel, UserModel
from app.schemas import IncomeCreate, IncomeResponse, IncomeUpdate
from app.security import get_current_user


router = APIRouter(prefix="/incomes", tags=["Incomes"])


# GET
@router.get("", response_model=list[IncomeResponse])
def get_incomes(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    statement = (
        select(IncomeModel)
        .where(IncomeModel.user_id == current_user.id)
        .order_by(IncomeModel.created_at.desc())
    )

    return db.scalars(statement).all()


# GET_ID
@router.get("/{income_id}", response_model=IncomeResponse)
def get_income(
    income_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    statement = select(IncomeModel).where(
        IncomeModel.id == income_id,
        IncomeModel.user_id == current_user.id
    )

    income = db.scalar(statement)

    if income is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="収入が見つかりません"
        )

    return income


# POST
@router.post(
    "",
    response_model=IncomeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_income(
    data: IncomeCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    income = IncomeModel(**data.model_dump(), user_id=current_user.id)

    db.add(income)
    db.commit()
    db.refresh(income)

    return income


# PATCH
@router.patch("/{income_id}", response_model=IncomeResponse)
def update_income(
    income_id: int,
    data: IncomeUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    statement = select(IncomeModel).where(
        IncomeModel.id == income_id,
        IncomeModel.user_id == current_user.id
    )

    income = db.scalar(statement)

    if income is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="収入が見つかりません"
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
        setattr(income, key, value)

    db.commit()
    db.refresh(income)

    return income


# 収入を削除
@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(
    income_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    statement = select(IncomeModel).where(
        IncomeModel.id == income_id,
        IncomeModel.user_id == current_user.id
    )

    income = db.scalar(statement)

    if income is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="収入が見つかりません"
        )

    db.delete(income)
    db.commit()