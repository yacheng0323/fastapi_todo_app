import os
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 優先使用 Railway 提供的 DATABASE_URL，否則使用個別環境變數組成
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # 本地開發環境配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "fastapi_todo_db")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(
    DATABASE_URL,
    echo=True,
    # PostgreSQL 特定配置
    pool_pre_ping=True,  # 連接前檢查
    pool_recycle=300,
)  # 連接回收時間


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
