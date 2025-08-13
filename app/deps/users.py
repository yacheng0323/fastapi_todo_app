from multiprocessing import AuthenticationError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session
from app.core.exceptions import NotFoundError
from app.db.session import get_session
from app.core.security import decode_access_token
from app.models.user import User, UserRole

from app.core.exceptions import AuthenticationError, NotFoundError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    """取得當前登入用戶"""
    try:
        # 解碼 JWT token
        payload = decode_access_token(token)
        if payload is None:
            raise AuthenticationError(
                message="無效的存取令牌", details={"token_type": "access_token"}
            )

        # 取得用戶 ID
        user_id_str: int = int(payload.get("sub"))
        if not user_id_str:
            raise AuthenticationError(
                message="令牌中缺少用戶 ID", details={"token_type": "access_token"}
            )

        try:
            user_id = int(user_id_str)
        except ValueError:
            raise AuthenticationError(
                message="令牌中的用戶 ID 格式無效",
                details={"token_type": "access_token"},
            )
    except JWTError as e:
        # 使用統一錯誤處理
        raise AuthenticationError(message="JWT 令牌解析失敗", details={"error": str(e)})

    # 從資料庫取得用戶
    user = session.get(User, user_id)
    if user is None:
        raise NotFoundError(
            resource="用戶", details={"user_id": user_id, "source": "access_token"}
        )

    return user


def required_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise AuthenticationError(
                message=f"需要 {required_role.value} 權限",
                details={
                    "required_role": required_role.value,
                    "current_role": current_user.role.value,
                    "user_id": current_user.id,
                },
            )
        return current_user

    return role_checker


def required_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise AuthenticationError(
            message="需要管理員權限",
            details={
                "required_role": "admin",
                "current_role": current_user.role.value,
                "user_id": current_user.id,
                "username": current_user.username,
            },
        )
    return current_user
