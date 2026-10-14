from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import ExpenseModel
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse


Base.metadata.create_all(bind=engine)


app = FastAPI()


# HOME
@app.get("/")
def home():
    return {"message": "家計簿API"}


# GET
@app.get("/exapenses", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    return db.scalars(
        select(ExpenseModel).order_by(ExpenseModel.id)
    ).all()


# GET_ID
@app.get("/exapenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(ExpenseModel, expense_id)
    
    if expense is None:
        raise HTTPException(status_code=404, detail="支出が見つかりません")
    
    return expense


# POST
@app.post(
    "/expenses", 
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
@app.patch("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int, 
    data: ExpenseUpdate,
    db: Session = Depends(get_db)
):
    expense = db.get(ExpenseModel, expense_id)
    
    if expense is None:
        raise HTTPException(status_code=404, detail="支出が見つかりません")
    
    update_data = data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if value is not None:
            setattr(expense, key, value)
            
    db.commit()
    db.refresh(expense)
    
    return expense


# DELETE
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(ExpenseModel, expense_id)
    
    if expense is None:
        raise HTTPException(status_code=404, detail="支出が見つかりません")
            
    db.delete(expense)
    db.commit()
    
    return {"message": "支出を削除しました"}