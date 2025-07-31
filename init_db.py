from app.db.session import engine
from app.models.todo import Todo
from app.models.user import User
from sqlmodel import SQLModel

def init():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    init()