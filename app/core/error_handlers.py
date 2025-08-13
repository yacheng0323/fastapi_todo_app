"""
全域錯誤處理器
攔截和處理應用程式中的所有例外
"""


import logging
from typing import Union
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError

from app.core.exceptions import AppException, ErrorCode


logger = logging.getLogger(__name__)

def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: dict = None,
) -> JSONResponse:
    """ 建立統一格式的錯誤回應"""
    return JSONResponse(
        status_code = status_code,
        content = {
            "success": False,
            "error_code": error_code,
            "message": message,
            "details": details or {},
        }
    )

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """ 處理自定義的應用程式例外"""
    logger.error(f"App Exception: {exc.error_code} - {exc.message}")
    return create_error_response(
        error_code = exc.error_code.value,
        message = exc.message,
        status_code = exc.status_code,
        details = exc.details,
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """ 處理 HTTP 例外"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")

    # 如果 detail 是字典格式 就直接使用
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code = exc.status_code,
            content = {
                "success": False,
                **exc.detail
            }
        )

    # 如果是字串，轉換為標準格式
    return create_error_response(
        error_code = "HTTP_ERROR",
        message = str(exc.detail),
        status_code = exc.status_code
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """ 處理資料驗證錯誤"""
    logger.warning(f"Validation error: {exc.errors()}")

    # 提取驗證錯誤詳細資訊
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    return create_error_response(
        error_code = ErrorCode.VALIDATION_ERROR.value,
        message = "資料驗證失敗",
        status_code = 422,
        details = {
            "errors": errors,
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """處理資料庫例外"""
    logger.error(f"Database error: {str(exc)}")
    
    return create_error_response(
        error_code=ErrorCode.DATABASE_ERROR.value,
        message="資料庫操作失敗",
        status_code=500,
        details={"error": str(exc)} if logger.level == logging.DEBUG else {}
    )

async def jwt_exception_handler(request: Request, exc: JWTError) -> JSONResponse:
    """處理 JWT 例外"""
    logger.warning(f"JWT error: {str(exc)}")
    
    return create_error_response(
        error_code=ErrorCode.INVALID_TOKEN.value,
        message="無效的認證令牌",
        status_code=401
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """處理所有其他未捕獲的例外"""
    logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}")
    
    return create_error_response(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        message="伺服器內部錯誤",
        status_code=500,
        details={"error": str(exc)} if logger.level == logging.DEBUG else {}
    )