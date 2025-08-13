from ast import Dict
from enum import Enum
from typing import Any, Optional, Dict

from fastapi import HTTPException


class ErrorCode(str, Enum):
    # 認證相關錯誤
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # 用戶相關錯誤
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

    # 相關 Todo 錯誤
    TODO_NOT_FOUND = "TODO_NOT_FOUND"
    TODO_ACCESS_DENIED = "TODO_ACCESS_DENIED"

    # 資料驗證錯誤
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"

    # 資料庫錯誤
    DATABASE_ERROR = "DATABASE_ERROR"

    # 一般錯誤
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"


# 自定義例外基類
class AppException(Exception):
    """應用程式基礎例外類別"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# 具體的例外類別
class AuthenticationError(AppException):
    """認證錯誤"""

    def __init__(
        self, message: str = "認證失敗", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_TOKEN,
            status_code=401,
            details=details,
        )


class PermissionError(AppException):
    """權限錯誤"""

    def __init__(
        self, message: str = "權限不足", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            status_code=403,
            details=details,
        )


class NotFoundError(AppException):
    """資源不存在錯誤"""

    def __init__(
        self, resource: str = "資源", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{resource} 不存在",
            error_code=ErrorCode.TODO_NOT_FOUND,
            status_code=404,
            details=details,
        )


class ValidationError(AppException):
    """資料驗證錯誤"""

    def __init__(
        self, message: str = "資料驗證失敗", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details=details,
        )


class DatabaseError(AppException):
    """資料庫錯誤"""

    def __init__(
        self, message: str = "資料庫操作失敗", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            details=details,
        )


# 便利函數 : 快速建立 HTTPException
def create_http_exception(
    status_code: int,
    message: str,
    error_code: ErrorCode,
    details: Optional[Dict[str, Any]] = None,
) -> HTTPException:
    """建立標準格式 HTTPException"""
    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code.value,
            "message": message,
            "details": details or {},
        },
    )


# 預定義的常用錯誤
def todo_not_found(todo_id: str) -> HTTPException:
    """Todo 不存在錯誤"""
    return create_http_exception(
        status_code=404,
        message="Todo 不存在",
        error_code=ErrorCode.TODO_NOT_FOUND,
        details={"todo_id": todo_id},
    )


def todo_access_denied(todo_id: str, user_id: int) -> HTTPException:
    """Todo 存取權限錯誤"""
    return create_http_exception(
        status_code=403,
        message="無權限存取此 Todo",
        error_code=ErrorCode.TODO_ACCESS_DENIED,
        details={"todo_id": todo_id, "user_id": user_id},
    )


def invalid_credentials() -> HTTPException:
    """無效認證錯誤"""
    return create_http_exception(
        status_code=401,
        message="用戶名或密碼錯誤",
        error_code=ErrorCode.INVALID_CREDENTIALS,
    )


def user_already_exists(username: str) -> HTTPException:
    """用戶已存在錯誤"""
    return create_http_exception(
        status_code=400,
        message="用戶名已存在",
        error_code=ErrorCode.USER_ALREADY_EXISTS,
        details={"username": username},
    )
