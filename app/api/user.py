from fastapi import APIRouter, FastAPI, Depends, Form,HTTPException,status
from sqlmodel import SQLModel, Session,select
from app.models.user import User,UserCreate,UserOut
from app.db.session import get_session
from app.core.security import create_refresh_token,verify_password,create_access_token,get_password_hash,decode_refresh_token
from app.deps.users import get_current_user

router = APIRouter()

@router.post("/register",response_model=UserOut)
def register(user_in:UserCreate, session:Session = Depends(get_session)):
    # 先檢查帳號是否存在
    existing_user = session.exec(select(User).where(User.username == user_in.username)).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="用戶名已存在")
    
    # 檢查email是否存在
    if user_in.email:
        existing_email = session.exec(select(User).where(User.email == user_in.email)).first()
        if existing_email:
            raise HTTPException(status_code=400,detail="Email已存在")
        
    user = User(username=user_in.username,email= user_in.email,hashed_password=get_password_hash(user_in.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    # 查找使用者
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password")
    
    # 驗證密碼
    # if not verify_password(password,user.hashed_password):
    #     raise HTTPException(status_code=401,detail="Invalid username or password")
    
    # 建立 token
    access_token = create_access_token({"sub": str(user.id),"role": user.role.value})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access_token,"refresh_token":refresh_token ,"token_type": "bearer"}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh")
def refresh_token(refresh_token: str = Form(...),session: Session = Depends(get_session)):
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    user = session.get(User,int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
    
    new_access_token = create_access_token({"sub": str(user.id),"role": user.role.value})
    return {"access_token": new_access_token,"token_type": "bearer"}