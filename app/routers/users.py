from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserModel, ExpenseModel
from app.schemas import (
    UserCreate, 
    UserUpdate, 
    UserResponse,
    UserPasswordUpdate
)
from app.security import hash_password, get_current_user, verify_password


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
        raise HTTPException(
            status_code=409, 
            detail="このメールアドレスは登録済みです"
        )
    
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
        
        raise HTTPException(
            status_code=409, 
            detail="このメールアドレスは登録済みです"
        )
    
    return user


# GET_ME
@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: UserModel = Depends(get_current_user)):
    return current_user


# PATCH
@router.patch("/me", response_model=UserResponse)
def update_current_user(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    update_data = data.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=422, 
            detail="更新する項目を指定してください"
        )
    
    if "email" in update_data:
        if update_data["email"] is None:
            raise HTTPException(
                status_code=422, 
                detail="メールアドレスは空にできません"
            )
        
        new_email = str(update_data["email"])
        
        existing_user = db.scalar(
            select(UserModel).where(
                UserModel.email == new_email,
                UserModel.id != current_user.id
            )
        )
        
        if existing_user is not None:
            raise HTTPException(
                status_code=409, 
                detail="このメールアドレスは登録済みです"
            )
        
        current_user.email = new_email
        
    try:
        db.commit()
        db.refresh(current_user)
        
    except IntegrityError:
        db.rollback()
        
        raise HTTPException(
            status_code=409, 
            detail="このメールアドレスは登録済みです"
        )
    
    return current_user


# PASSWORD_PATCH
@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def update_current_user_password(
    data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 現在のパスワードを確認
    if not verify_password(
        data.current_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="現在のパスワードが正しくありません"
        )
        
    # 新しいパスワードが現在のものと同じでないか確認
    if verify_password(
        data.new_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新しいパスワードは現在のものと別のものにしてください"
        )
        
    # 新しいパスワードをハッシュ化して保存
    current_user.hashed_password = hash_password(data.new_password)
    
    db.commit()


# DELETE
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)    
):
    # アカウント削除時に本人の支出も削除

    db.execute(
        delete(ExpenseModel).where(
            ExpenseModel.user_id == current_user.id
        )
    )
    
    db.delete(current_user)
    db.commit()