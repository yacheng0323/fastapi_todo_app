from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

class TodoBase(SQLModel):
    title: str
    description: Optional[str] = None

class Todo(TodoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,primary_key=True)

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    pass

class TodoOut(TodoBase):
    id: uuid.UUID