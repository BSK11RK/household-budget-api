from fastapi import FastAPI

from app.database import Base, engine
from app.models import ExpenseModel, UserModel
from app.routers import expenses, users, auth


# モデルを読み込んでからテーブルを作成
Base.metadata.create_all(bind=engine)


app = FastAPI(title="家計簿API")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(expenses.router)