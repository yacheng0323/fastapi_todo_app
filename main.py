from fastapi import FastAPI
from app.api import todo,user

app = FastAPI()

app.include_router(todo.router,prefix="/todos",tags=["Todo"])
app.include_router(user.router,prefix="/users",tags=["Users"])