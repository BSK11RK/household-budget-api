from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ExpenseModel, UserModel
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.security import get_current_user


router = APIRouter(prefix="/expenses", tags=["Expenses"])


# GET
@router.get("", response_model=list[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    statement = select(ExpenseModel).where(
        ExpenseModel.user_id == current_user.id
    )

    return db.scalars(statement).all()


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
        raise HTTPException(status_code=404, detail="支出が見つかりません")
    
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
        raise HTTPException(status_code=404, detail="支出が見つかりません")
    
    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in data.model_dump(exclude_unset=True).items():
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
        raise HTTPException(status_code=404, detail="支出が見つかりません")
    
    db.delete(expense)
    db.commit()