import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import UserModel
from app.security import get_current_user


# テスト専用のインメモリSQLiteデータベース
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture
def client():
    # テストごとにテーブルを作成
    Base.metadata.create_all(bind=test_engine)
    
    db = TestingSessionLocal()
    
    test_user = UserModel(
        id=1,
        email="test@example.com",
        hashed_password="test-password-hash"
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # テスト中はテスト用データベースを使う
    def override_get_db():
        try:
            yield db
        finally:
            pass
        
    # JWT認証をテスト用ユーザーに置き換える
    def override_get_current_user():
        return test_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        
        db.close()
        
        Base.metadata.drop_all(bind=test_engine)