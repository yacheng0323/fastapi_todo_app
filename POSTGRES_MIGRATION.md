# PostgreSQL 遷移指南

## 前置準備

### 1. 安裝 PostgreSQL
- **Windows**: 從 [PostgreSQL 官網](https://www.postgresql.org/download/windows/) 下載安裝
- **macOS**: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`

### 2. 啟動 PostgreSQL 服務
- **Windows**: 服務通常會自動啟動
- **macOS**: `brew services start postgresql`
- **Linux**: `sudo systemctl start postgresql`

### 3. 創建資料庫用戶（可選）
```sql
-- 以 postgres 用戶身份登入
sudo -u postgres psql

-- 創建新用戶
CREATE USER your_username WITH PASSWORD 'your_password';
ALTER USER your_username CREATEDB;
```

## 遷移步驟

### 1. 安裝新依賴
```bash
pip install -r requirements.txt
```

### 2. 配置環境變數
複製 `.env.example` 到 `.env` 並填入正確的資料庫資訊：
```env
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_todo_db
# 或分別設置
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=fastapi_todo_db
```

### 3. 創建資料庫
```bash
python setup_postgres.py
```

### 4. 執行資料庫遷移
```bash
# 初始化 Alembic（如果需要）
alembic stamp head

# 執行遷移
alembic upgrade head
```

### 5. 資料遷移（從 SQLite）
如果你需要從 SQLite 遷移資料：

```python
# 創建 migrate_data.py
import sqlite3
import psycopg2
from app.db.session import engine
from sqlmodel import Session

def migrate_users():
    # SQLite 連接
    sqlite_conn = sqlite3.connect('todos.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # PostgreSQL 連接
    with Session(engine) as session:
        # 遷移用戶資料
        sqlite_cursor.execute("SELECT * FROM user")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            # 插入到 PostgreSQL
            # 根據你的模型調整
            pass
```

### 6. 測試
```bash
python -m pytest  # 如果有測試
python main.py     # 啟動應用
```

## 注意事項

1. **UUID 處理**: PostgreSQL 對 UUID 的處理與 SQLite 不同，確保模型正確
2. **時間戳**: PostgreSQL 有更嚴格的時間戳處理
3. **外鍵約束**: PostgreSQL 對外鍵約束更嚴格
4. **大小寫敏感**: PostgreSQL 對大小寫敏感,test

## 常見問題

### 連接失敗
- 檢查 PostgreSQL 服務是否運行
- 確認防火牆設置
- 檢查 `pg_hba.conf` 認證設置

### 權限問題
- 確保用戶有創建資料庫的權限
- 檢查表的 CRUD 權限 