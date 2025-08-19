# Railway 部署指南

## 部署问题解决方案

基于 FastAPI 和 Railway 官方文档分析，以下是解决 URL 调用失败问题的完整解决方案：

## 1. 主要问题分析

- **主机绑定问题**: 必须绑定到 `0.0.0.0` 而不是 `localhost`
- **端口配置**: 必须使用 Railway 提供的 `PORT` 环境变量
- **数据库连接**: 需要支持 Railway 的 `DATABASE_URL` 格式
- **缺少部署配置**: 需要 Procfile 或 railway.json

## 2. 修复内容

### A. 创建了部署配置文件

#### Procfile
```
web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

#### railway.json
```json
{
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
```

#### nixpacks.toml
```toml
[variables]
PYTHON_VERSION = "3.11"

[phases.setup]
nixPkgs = ["python311", "pip"]

[phases.install]
cmds = [
    "pip install --upgrade pip",
    "pip install -r requirements.txt"
]

[phases.build]
cmds = [
    "alembic upgrade head"
]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"
```

### B. 修复了数据库连接配置

更新了 `app/db/session.py` 以支持 Railway 的 `DATABASE_URL` 环境变量：

```python
# 优先使用 Railway 提供的 DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # 本地开发环境配置
    DB_HOST = os.getenv("DB_HOST","localhost")
    # ... 其他配置
```

### C. 优化了生产环境配置

更新了 `main.py` 中的 uvicorn 配置：

```python
uvicorn.run(
    "main:app", 
    host="0.0.0.0", 
    port=port, 
    reload=False,
    workers=1,  # Railway 建议单个容器使用单个 worker
    access_log=True,
    log_level="info"
)
```

## 3. Railway 部署步骤

### 方法 1: GitHub 部署 (推荐)

1. 将代码推送到 GitHub 仓库
2. 在 Railway 控制台创建新项目
3. 选择 "Deploy from GitHub repo"
4. 连接你的 GitHub 账户并选择仓库
5. 配置环境变量（见下文）
6. 部署完成后生成公共域名

### 方法 2: CLI 部署

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 在项目目录初始化
railway init

# 部署
railway up

# 生成公共域名
railway domain
```

## 4. 必需的环境变量配置

在 Railway 项目的 Variables 部分设置以下环境变量：

### 数据库配置
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### 应用配置
```
PORT=${{RAILWAY_PORT}}
```

### JWT 相关 (如果需要)
```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 5. 常见问题解决

### 问题 1: 应用无法响应
- **原因**: 主机绑定不正确
- **解决**: 确保使用 `--host 0.0.0.0`

### 问题 2: 端口错误
- **原因**: 未使用 Railway 提供的 PORT 环境变量
- **解决**: 使用 `${PORT}` 或 `os.getenv("PORT")`

### 问题 3: 数据库连接失败
- **原因**: 数据库 URL 格式不正确
- **解决**: 使用 `${{Postgres.DATABASE_URL}}` 引用

### 问题 4: 健康检查失败
- **原因**: 健康检查端点不可用
- **解决**: 确保 `/health` 端点正常工作

## 6. 验证部署

部署成功后，你应该能够访问：

- 主页: `https://your-app.up.railway.app/`
- 健康检查: `https://your-app.up.railway.app/health`
- API 文档: `https://your-app.up.railway.app/docs`
- 待办事项 API: `https://your-app.up.railway.app/todos/`

## 7. 监控和调试

使用 Railway CLI 查看日志：
```bash
railway logs
```

或在 Railway 控制台的 Deployments 页面查看实时日志。

## 8. 性能优化建议

1. **单 Worker**: Railway 建议每个容器使用单个 uvicorn worker
2. **连接池**: 已配置 PostgreSQL 连接池优化
3. **健康检查**: 设置合理的健康检查超时时间
4. **日志级别**: 生产环境使用 "info" 级别

## 总结

通过以上修复，你的 FastAPI 应用现在应该能够在 Railway 上正常部署和运行。关键是确保：

1. 正确的主机和端口绑定
2. 支持 Railway 的环境变量格式
3. 适当的生产环境配置
4. 完整的部署配置文件

如果仍有问题，请检查 Railway 部署日志以获取更多详细信息。
