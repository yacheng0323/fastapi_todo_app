"""
PostgreSQL 資料庫設置腳本
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os 
from dotenv import load_dotenv

load_dotenv()


from app.db.session import DB_HOST, DB_NAME, DB_PORT, DB_USER

# 載入環境變數

def create_database():
    """創建 PostgreSQL 資料庫"""
    DB_HOST = os.getenv("DB_HOST","localhost")
    DB_PORT = os.getenv("DB_PORT","5432")
    DB_USER = os.getenv("DB_USER","postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD","")
    DB_NAME = os.getenv("DB_NAME","fastapi_todo_db")

    try:
        # 連接到 PostgreSQL (連接到 postgres 預設資料庫)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres" # 這行很重要?
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # 檢查資料庫是否已存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()

        if not exists:
            # 創建資料庫
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"資料庫 '{DB_NAME}' 已成功創建")
        else:
            print(f"資料庫 '{DB_NAME}' 已經存在")

        cursor.close()
        conn.close()

        return True
    
    except psycopg2.Error as e:
        print(f"資料庫創建失敗: {e}")
        print("請確認：")
        print("1. PostgreSQL 服務已啟動")
        print("2. 連接參數正確")
        print("3. 用戶有創建資料庫的權限")
        return False

def test_connection():
    """測試資料庫連接"""
    
    DB_PASSWORD = os.getenv("DB_PASSWORD","")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        print("資料庫連接成功")
        return True
    except psycopg2.Error as e:
        print(f"資料庫連接失敗: {e}")
        return False

if __name__ == "__main__":
    print("PostgreSQL 資料庫設置")
    print("=" * 40)

    # 創建資料庫
    if create_database():
        test_connection()

        print("\n下一步：")
        print("1. 執行 pip install -r requirements.txt")
        print("2. 執行 alembic upgrade head")
        print("3. 啟動應用程式")
