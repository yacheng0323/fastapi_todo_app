from sqlmodel import SQLModel, Session,create_engine

DATABASE_URL = "sqlite:///./todos.db"
engine = create_engine(DATABASE_URL,echo=True)

def get_session():
    with Session(engine) as session:
        yield session