from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


app = FastAPI()


# 支出データの入力形式
class ExpenseCreate(BaseModel):
    title: str
    amount: int = Field(gt=0)
    category: str
    
    
class ExpenseUpdate(BaseModel):
    title: str | None = None
    amount: int | None = Field(default=None, gt=0)
    category: str | None = None
    
    
# 仮のデータ
expenses = []

next_expense_id = 1


# HOME
@app.get("/")
def home():
    return {"message": "家計簿API"}


# GET
@app.get("/exapenses")
def get_expenses():
    return expenses


# GET_ID
@app.get("/exapenses/{expense_id}")
def get_expense(expense_id: int):
    for expense in expenses:
        if expense["id"] == expense_id:
            return expense
        
    raise HTTPException(status_code=404, detail="支出が見つかりません")


# POST
@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(data: ExpenseCreate):
    global next_expense_id
    
    new_expense = {
        "id": next_expense_id,
        **data.model_dump()
    }
    
    expenses.append(new_expense)
    next_expense_id += 1
    
    return new_expense


# PATCH
@app.patch("/expenses/{expense_id}")
def update_expense(expense_id: int, data: ExpenseUpdate):
    for expense in expenses:
        if expense["id"] == expense_id:
            update_data = data.model_dump(exclude_unset=True)
            
            for key, value in update_data.items():
                if value is not None:
                    expense[key] = value
                    
            return expense
        
    raise HTTPException(status_code=404, detail="支出が見つかりません")


# DELETE
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    for index, expense in enumerate(expenses):
        if expense["id"] == expense_id:
            deleted_expense = expenses.pop(index)
            
            return {
                "message": "支出を削除しました",
                "deleted": deleted_expense
            }

    raise HTTPException(status_code=404, detail="支出が見つかりません")