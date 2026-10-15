import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserModel


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY が設定されていません。.env を確認してください")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# パスワードをハッシュ化
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# パスワードが一致するか検証
def verify_password(plain_password:str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# JWTアクセストークンを発行
def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    payload = {"sub": str(user_id), "exp": expires_at}
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# トークンを検証し、ログインユーザーを取得
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効か、有効期限が切れています",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        subject = payload.get("sub")
        
        if not isinstance(subject, str):
            raise credentials_exception
        
        user_id = int(subject)
        
    except (InvalidTokenError, ValueError):
        raise credentials_exception
    
    user = db.get(UserModel, user_id)
    
    if user is None:
        raise credentials_exception
    
    return user