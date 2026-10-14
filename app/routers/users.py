from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserModel
from app.schemas import UserCreate, UserResponse
from app.security import hash_password


router = APIRouter(prefix="/users", tags=["Users"])


# POST
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.scalar(
        select(UserModel).where(UserModel.email == str(data.email))
    )
    
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="このメールアドレスは登録済みです")
    
    user = UserModel(
        email=str(data.email),
        hashed_password=hash_password(data.password)
    )
    
    db.add(user)
    
    try:
        db.commit()
        db.re(user)
        
    except IntegrityError:
        db.rollback()
        
        raise HTTPException(status_code=409, detail="このメールアドレスは登録済みです")
    
    return user