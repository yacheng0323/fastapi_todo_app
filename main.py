from fastapi import FastAPI
from app.api import todo,user

app = FastAPI(
    title="FastAPI Todo App",
    description="練習使用 PostgreSQL 的 Todo 應用程式",
    version="1.0.0",
)

app.include_router(todo.router,prefix="/todos",tags=["Todo"])
app.include_router(user.router,prefix="/users",tags=["Users"])

@app.get("/")
async def root():
    return {"message": "歡迎使用 FastAPI Todo App with PostgreSQL!", "status": "running","database": "postgresql"}

@app.get("/health")
async def health_check():
    return {"status": "healthy","database": "postgresql","migrations": "managed by alembic"}