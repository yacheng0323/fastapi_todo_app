"""
PostgreSQL 資料庫設置與初始化腳本
整合 Alembic migrations 的完整環境設置工具
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os 
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

def get_db_config():
    """獲取資料庫配置"""
    return {
        'host': os.getenv("DB_HOST", "localhost"),
        'port': os.getenv("DB_PORT", "5432"),
        'user': os.getenv("DB_USER", "postgres"),
        'password': os.getenv("DB_PASSWORD", ""),
        'database': os.getenv("DB_NAME", "fastapi_todo_db")
    }

def create_database():
    """創建 PostgreSQL 資料庫"""
    config = get_db_config()
    
    try:
        # 連接到 postgres 預設資料庫
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # 檢查資料庫是否已存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config['database']}'")
        exists = cursor.fetchone()

        if not exists:
            # 創建資料庫
            cursor.execute(f"CREATE DATABASE {config['database']}")
            print(f"✅ 資料庫 '{config['database']}' 已成功創建")
        else:
            print(f"ℹ️  資料庫 '{config['database']}' 已經存在")

        cursor.close()
        conn.close()
        return True
    
    except psycopg2.Error as e:
        print(f"❌ 資料庫創建失敗: {e}")
        print("\n請確認：")
        print("1. PostgreSQL 服務已啟動")
        print("2. 連接參數正確（檢查 .env 檔案）")
        print("3. 用戶有創建資料庫的權限")
        return False

def test_connection():
    """測試資料庫連接"""
    config = get_db_config()
    database_url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

    try:
        conn = psycopg2.connect(database_url)
        conn.close()
        print("✅ 資料庫連接成功")
        return True
    except psycopg2.Error as e:
        print(f"❌ 資料庫連接失敗: {e}")
        return False

def run_migrations():
    """執行 Alembic migrations"""
    try:
        print("🔄 執行資料庫 migrations...")
        result = subprocess.run(["alembic", "upgrade", "head"], 
                              capture_output=True, text=True, check=True)
        print("✅ Migrations 執行成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migrations 執行失敗: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ 找不到 alembic 命令，請確認已安裝 alembic")
        return False

def create_admin_user():
    """提示創建管理員用戶"""
    print("\n📋 建議創建管理員用戶：")
    print("1. 啟動應用：python -m uvicorn main:app --reload")
    print("2. 訪問：http://localhost:8000/docs")
    print("3. 註冊用戶後，手動在資料庫中將 role 改為 'admin'")
    print("   SQL: UPDATE \"user\" SET role = 'admin' WHERE username = 'your_admin_username';")

def main():
    """主函數：完整的環境設置流程"""
    print("🚀 PostgreSQL + FastAPI Todo App 環境設置")
    print("=" * 60)
    
    # 步驟 1：創建資料庫
    print("\n📦 步驟 1：創建資料庫")
    if not create_database():
        sys.exit(1)
    
    # 步驟 2：測試連接
    print("\n🔌 步驟 2：測試資料庫連接")
    if not test_connection():
        sys.exit(1)
    
    # 步驟 3：執行 migrations
    print("\n🗄️  步驟 3：執行資料庫結構遷移")
    if not run_migrations():
        print("⚠️  Migrations 失敗，請手動執行：alembic upgrade head")
        sys.exit(1)
    
    # 步驟 4：提示後續步驟
    print("\n🎉 環境設置完成！")
    print("\n📋 後續步驟：")
    print("1. 啟動應用：python -m uvicorn main:app --reload")
    print("2. 訪問 API 文檔：http://localhost:8000/docs")
    print("3. 註冊第一個用戶")
    
    create_admin_user()

if __name__ == "__main__":
    main()