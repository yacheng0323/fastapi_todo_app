import os

# 可自由修改這裡
module_name = "main"  # app 資料夾下的 main.py
app_instance = "app"
port = 8000
reload = True

# 組合 uvicorn 指令
command = f"uvicorn {module_name}:{app_instance} --port {port}"
if reload:
    command += " --reload"

print(f"🚀 Running: {command}")
os.system(command)