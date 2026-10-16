from fastapi import FastAPI

from app.routers import expenses, users, auth


app = FastAPI(title="家計簿API")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(expenses.router)