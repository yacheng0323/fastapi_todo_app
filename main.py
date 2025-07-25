from fastapi import FastAPI
from app.api import todo

app = FastAPI()

app.include_router(todo.router,prefix="/todos",tags=["Todo"])
