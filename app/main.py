from fastapi import FastAPI

from app.routers import expenses, users, auth, incomes, reports, budgets


app = FastAPI(title="家計簿API")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(incomes.router)
app.include_router(expenses.router)
app.include_router(reports.router)
app.include_router(budgets.router)