from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ExpenseModel
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.security import get_current_user


router = APIRouter(
    prefix="/expenses", 
    tags=["Expenses"],
    dependencies=[Depends(get_current_user)]
)


# GET
@router.get("", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    return db.scalars(select(ExpenseModel)).all()


# GET_ID
@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(ExpenseModel, expense_id)
    
    if expense is None:
        raise HTTPException(status_code=404, detail="支出が見つかりません")
    
    return expense


# POST
@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_expense(data: ExpenseCreate, db: Session = Depends(get_db)):
    expense = ExpenseModel(**data.model_dump())
    
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    return expense


# PATCH
@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db)
):
    expense = db.get(ExpenseModel, expense_id)
    
    if expense is None:
        raise HTTPException(status_code=404, detail="支出が見つかりません")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(expense, key, value)
        
    db.commit()
    db.refresh(expense)
    
    return expense


# DELETE
@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(ExpenseModel, expense_id)
    
    if expense is None:
        raise HTTPException(status_code=404, detail="支出が見つかりません")
    
    db.delete(expense)
    db.commit()