from typing import Optional,List,TYPE_CHECKING
from enum import Enum
from sqlmodel import SQLModel, Field, Column, Enum as SQLEnum,Relationship

if TYPE_CHECKING:
    from .todo import Todo

# 1. 定義用戶角色
class UserRole(str, Enum):
    admin = "admin"
    user = "user"

# 2. 資料庫中的用戶表格
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True)  # 改為 unique，不是 primary_key
    email: Optional[str] = Field(default=None)
    hashed_password: str
    role: UserRole = Field(sa_column=Column(SQLEnum(UserRole)), default=UserRole.user)

    # 關係
    todos: List["Todo"] = Relationship(back_populates="user")

# 3. 註冊時接收的資料
class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    email: Optional[str] = Field(default=None, regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(min_length=6)

# 4. 回傳給前端的資料（不包含密碼）
class UserOut(SQLModel):
    id: int
    username: str
    email: Optional[str] = None
    role: UserRole  # 改為 UserRole 類型

# 5. 包含 todos 的用戶資料 (管理員用
class UserOutWithTodos(UserOut):
    todos: List["Todo"] = []