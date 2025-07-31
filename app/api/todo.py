from fastapi import APIRouter,Depends,HTTPException
from sqlmodel import select
from app.models.todo import Todo,TodoCreate,TodoOut,TodoUpdate
from app.db.session import get_session
from sqlmodel import Session
import uuid

router = APIRouter()

@router.post("/",response_model=TodoOut)
def create_todo(todo: TodoCreate,session: Session = Depends(get_session)):
    db_todo = Todo(**todo.dict())
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@router.get("/",response_model=list[TodoOut])
def read_todos(session: Session = Depends(get_session)):
    todos = session.exec(select(Todo)).all()
    return todos

@router.get("/{todo_id}",response_model=TodoOut)
def read_todo(todo_id: uuid.UUID,session: Session = Depends(get_session)):
    todo = session.get(Todo,todo_id)
    if not todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    return todo;

@router.put("/{todo_id}",response_model=TodoOut)
def update_todo(todo_id: uuid.UUID,updated_todo: TodoUpdate,session: Session = Depends(get_session)):
    todo = session.get(Todo,todo_id)
    if not todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    for key,value in updated_todo.dict(exclude_unset=True).items():
        setattr(todo,key,value)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.delete("/{todo_id}")
def delete_todo(todo_id: uuid.UUID, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return {"msg": "Deleted"}