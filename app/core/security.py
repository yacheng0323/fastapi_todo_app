from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt,JWTError
import os
from dotenv import load_dotenv
# 載入 .env 檔案的變數
load_dotenv() 

# 建立密碼加密器
pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")



SECRET_KEY = os.getenv("SECRET_KEY","default_key_if_missing")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 建立 JWT token
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire,"type": "access"})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

# 刷新 JWT token
def create_refresh_token(data: dict,expires_delta : timedelta=None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp":expire,"type":"refresh"})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

# 解碼 access_token
def decode_access_token(token:str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if  payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None

# 解碼 refresh_token
def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None