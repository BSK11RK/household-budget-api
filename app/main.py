from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import Base, engine, get_db
from app.models import ExpenseModel, UserModel
from app.schemas import (
    ExpenseCreate, 
    ExpenseUpdate, 
    ExpenseResponse,
    UserCreate,
    UserResponse
)
from app.security import hash_password


Base.metadata.create_all(bind=engine)


app = FastAPI()


# HOME
@app.get("/")
def home():
    return {"message": "家計簿API"}


# USser
# POST
@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    # メールアドレスの重複を確認
    existing_user = db.scalar(
        select(UserModel).where(
            UserModel.email == str(data.email)
        )
    )
    
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="このメールアドレスは登録済みです")
    
    # パスワードをハッシュ化
    user = UserModel(
        email=str(data.email),
        hashed_password=hash_password(data.password)
    )
    
    db.add(user)
    
    try:
        db.commit()
        db.refresh(user)
    
    except IntegrityError:
        # 同時登録などで重複した場合にも対応
        db.rollback()
        
        raise HTTPException(status_code=400, detail="このメールアドレスは登録済みです")
    
    return user


# Expense
# GET
@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    return db.scalars(
        select(ExpenseModel).order_by(ExpenseModel.id)
    ).all()


# GET_ID
@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
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