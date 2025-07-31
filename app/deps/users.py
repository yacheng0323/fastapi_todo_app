from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from sqlmodel import SQLModel,Session,select
from app.db.session import get_session
from app.core.security import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(session: Session = Depends(get_session),token: str = Depends(oauth2_scheme),)-> User:
    # 取得當前登入用戶
    try:
        # 解碼 JWT token
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="無效 token")

        # 取得用戶 ID
        user_id: int = int(payload.get("sub"))
    except (JWTError,ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="無效 token")
    
    # 從資料庫取得用戶
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用戶不存在")
    return user

def required_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(status_code=403,detail=f"需要 {required_role.value} 權限")
        return current_user
    return role_checker

def required_admin(current_user: User = Depends(get_current_user)) -> User:
    if (current_user.role != UserRole.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="需要管理員權限")
    return current_user