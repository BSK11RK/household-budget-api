from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr


# User
# ユーザー登録
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    

# ユーザーの更新
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    

# ユーザーのレスポンス    
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
# ログイン結果
class Token(BaseModel):
    access_token: str
    token_type: str


# Expense
# 支出の登録
class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    amount: int = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)
    

# 支出の更新
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
    

# 支出のレスポンス
class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    amount: int
    category: str
    user_id: int
    created_at: datetime
    updated_at: datetime