from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserModel
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.security import hash_password, get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


# GET
@router.get("", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.scalars(select(UserModel)).all()


# GET_ME
@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: UserModel = Depends(get_current_user)):
    return current_user


# GET_ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(UserModel, user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    
    return user


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
        db.refresh(user)
        
    except IntegrityError:
        db.rollback()
        
        raise HTTPException(status_code=409, detail="このメールアドレスは登録済みです")
    
    return user


# PATCH
@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.get(UserModel, user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    
    update_data = data.model_dump(exclude_unset=True)
    
    if "email" in update_data:
        if update_data["email"] is None:
            raise HTTPException(status_code=422, detail="メールアドレスは空にできません")
        
        update_data["email"] = str(update_data["email"])
        
        existing_user = db.scalar(
            select(UserModel).where(
                UserModel.email == update_data["email"],
                UserModel.id != user_id
            )
        )
        
        if existing_user is not None:
            raise HTTPException(status_code=409, detail="このメールアドレスは登録済みです")
        
    for key, value in update_data.items():
        setattr(user, key, value)
        
    try:
        db.commit()
        db.refresh(user)
        
    except IndentationError:
        db.rollback()
        
        raise HTTPException(status_code=409, detail="このメールアドレスは登録済みです")
    
    return user


# DELETE
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(UserModel, user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    
    db.delete(user)
    db.commit()