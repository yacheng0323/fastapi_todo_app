from typing import Optional
from sqlmodel import SQLModel,Field
import uuid

class UserBase(SQLModel):
    username: str
    email: Optional[str] = None

class User(UserBase, table = True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str

class UserCreate(UserBase):
    password: str

class UserOut(SQLModel):
    id: int
    username: str
    email: Optional[str] = None
