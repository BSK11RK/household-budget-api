from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr


# User
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    
 
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    

# パスワードの更新
class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
    
    
# Token
class Token(BaseModel):
    access_token: str
    token_type: str
    
    
# Income
class IncomeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    amount: int = Field(gt=0)
    source: str = Field(min_length=1, max_length=50)
    
    
class IncomeUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )
    amount: int | None = Field(default=None, gt=0)
    source: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )
    
    
class IncomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    amount: int
    source: str
    user_id: int
    created_at: datetime
    updated_at: datetime


# Expense
class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    amount: int = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)
    

class ExpenseUpdate(BaseModel):
    title: str | None = Field(
        default=None, 
        min_length=1, 
        max_length=100
    )
    amount: int | None = Field(default=None, gt=0)
    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )
    

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    amount: int
    category: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    
# 月別集計のレスポンス
class MonthlySummary(BaseModel):
    year: int
    month: int
    total: int
    
    
# カテゴリ別集計の1項目
class CategorySummaryItem(BaseModel):
    category: str
    total: int
    
    
# 月ごとの推移の1項目
class MonthlyTrendItem(BaseModel):
    month: int
    total: int
    
    
class MonthlyReport(BaseModel):
    year: int
    month: int
    income_total: int
    expense_total: int
    balance: int
    
    
class CategoryExpenseTotal(BaseModel):
    category: str
    total: int
    
    
class MonthlyCategoryReport(BaseModel):
    year: int
    month: int
    categories: list[CategoryExpenseTotal]