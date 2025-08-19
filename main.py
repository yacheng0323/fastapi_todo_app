import os
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError
from fastapi import HTTPException


from app.api import todo, user
from app.core.exceptions import AppException
from app.core.error_handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    jwt_exception_handler,
    general_exception_handler,
)

app = FastAPI(
    title="FastAPI Todo App",
    description="練習使用 PostgreSQL 的 Todo 應用程式",
    version="1.0.0",
)

# ===== 註冊錯誤處理器 =====
# 自定義應用程式例外
app.add_exception_handler(AppException, app_exception_handler)

# FastAPI 內建例外
app.add_exception_handler(HTTPException, http_exception_handler)

# 資料驗證例外
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 資料庫例外
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

# JWT 例外
app.add_exception_handler(JWTError, jwt_exception_handler)

# 其他例外
app.add_exception_handler(Exception, general_exception_handler)

# ===== 註冊路由 =====
app.include_router(todo.router, prefix="/todos", tags=["Todo"])
app.include_router(user.router, prefix="/users", tags=["Users"])
# app.include_router(search.router,prefix="/search",tags=["Search"])


@app.get("/")
async def root():
    return {
        "message": "歡迎使用 FastAPI Todo App with PostgreSQL!",
        "status": "running",
        "database": "postgresql",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "postgresql",
        "migrations": "managed by alembic",
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Railway 會提供 PORT 環境變數
    # 生產環境配置
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,  # Railway 建議單個容器使用單個 worker
        access_log=True,
        log_level="info",
    )
