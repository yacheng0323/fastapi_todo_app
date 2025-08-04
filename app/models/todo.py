from typing import Optional,TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .user import User

class TodoBase(SQLModel):
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None,max_length=1000)
    is_completed: bool = Field(default=False)

class Todo(TodoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # 關係
    user: "User" = Relationship(back_populates="todos")

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    title: Optional[str] = Field(default=None,max_length=200)
    description: Optional[str] = Field(default=None,max_length=1000)
    is_completed: Optional[bool] = Field(default=None)

class TodoOut(TodoBase):
    id: uuid.UUID
    user_id: int
    created_at: datetime
    updated_at: datetime

class TodoOutWithUser(TodoOut):
     # 管理員查看時顯示用戶信息
    user: Optional["User"] = None