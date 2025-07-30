from fastapi import APIRouter, FastAPI, Depends, Form,HTTPException
from sqlmodel import SQLModel, Session,select
from app.models.user import User,UserCreate,UserOut
from app.db.session import get_session
from app.core.security import verify_password,create_access_token,get_password_hash


router = APIRouter()

@router.post("/register",response_model=UserOut)
def register(user_in:UserCreate, session:Session = Depends(get_session)):
    # 先檢查帳號是否存在
    existing_user = session.exec(select(User).where(User.username == user_in.username)).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="Username already registered")
    
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
    if not user:
        raise HTTPException(status_code=401,detail="Invalid username or password")
    
    # 驗證密碼
    if not verify_password(password,user.hashed_password):
        raise HTTPException(status_code=401,detail="Invalid username or password")
    
    # 建立 token
    token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}
