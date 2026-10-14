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