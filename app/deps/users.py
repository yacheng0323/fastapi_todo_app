from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from sqlmodel import SQLModel,Session,select
from app.db.session import get_session
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(session: Session = Depends(get_session),token: str = Depends(oauth2_scheme))-> User:
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
        user_id: int = int(payload.get("sub"))
    except (JWTError,ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    
    user = session.get(User,int(payload.get("sub")))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
    return user

def required_role(required_role: str):
    def checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403,detail="Insufficient permissions")
        return user
    return checker