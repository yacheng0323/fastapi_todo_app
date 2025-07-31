from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Column, Enum as SQLEnum, Relationship
from datetime import datetime
import uuid

class UserBase(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    email: Optional[str] = Field(default=None, regex=r'^[^@]+@[^@]+\.[^@]+$')

class UserRole(str, Enum):
    admin = "admin"
    user = "user"

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str
    role: UserRole = Field(sa_column=Column(SQLEnum(UserRole)), default=UserRole.user)

class UserCreate(UserBase):
    password: str

class UserOut(SQLModel):
    id: int
    username: str
    email: Optional[str] = None

