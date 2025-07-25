from app.db.session import engine
from app.models.todo import SQLModel

SQLModel.metadata.create_all(engine)