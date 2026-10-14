from pydantic import BaseModel, ConfigDict, Field


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