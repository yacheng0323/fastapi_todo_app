import datetime
from typing import Optional
from fastapi import APIRouter,Depends,HTTPException
from sqlmodel import select,Session
from app.deps.users import get_current_user, required_admin
from app.models.todo import SimpleUserInfo, Todo,TodoCreate,TodoOut, TodoOutWithUser,TodoUpdate
from app.db.session import get_session
from sqlalchemy import func,or_
import uuid

from app.models.user import User

# 導入統一錯誤處理
from app.core.exceptions import todo_not_found, todo_access_denied, NotFoundError, PermissionError

router = APIRouter()

@router.post("/",response_model=TodoOut)
def create_todo(todo: TodoCreate,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    """創建新的 todo - 自動關連到當前用戶"""
    try:
        db_todo = Todo(**todo.model_dump(),user_id=current_user.id)
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)
        return db_todo
    except Exception as e:
        session.rollback()
        # 丟出我們的自定義例外，會被全域處理器捕獲
        raise NotFoundError(resource="Todo", details={"error": str(e)})
    

@router.get("/",response_model=list[TodoOut])
def read_todos(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """ 獲取當前用戶的所有 todos - 用戶隔離 """
    todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    return todos

@router.get("/{todo_id}",response_model=TodoOut)
def read_todo(todo_id: uuid.UUID,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    """ 獲取特定 todo - 檢查所有權 """
    todo = session.get(Todo,todo_id)
    if not todo:
        # 使用統一錯誤處理
        raise todo_not_found(str(todo_id))
    
    # 🛡️ 檢查所有權：用戶只能訪問自己的 todo
    if todo.user_id != current_user.id:
        # 使用統一錯誤處理
        raise todo_access_denied(str(todo_id),current_user.id)
    
    return todo

@router.put("/{todo_id}",response_model=TodoOut)
def update_todo(todo_id: uuid.UUID,updated_todo: TodoUpdate,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    """ 更新 todo - 檢查所有權並自動更新時間戳記 """
    todo = session.get(Todo,todo_id)
    if not todo:
        # 使用統一錯誤處理
        raise todo_not_found(str(todo_id))

    # 檢查所有權:用戶只能更新自己的 todo
    if todo.user_id != current_user.id:
        raise todo_access_denied(str(todo_id),current_user.id)

    try:
        # 更新字段
        for key,value in updated_todo.model_dump(exclude_unset=True).items():
            setattr(todo,key,value)

        todo.updated_at = datetime.datetime.now()

        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo
    except Exception as e:
        session.rollback()
        # 如果更新失敗，丟出自定義例外
        raise NotFoundError(resource="Todo 更新",details={"todo_id": str(todo_id), "error": str(e)})
    

@router.delete("/{todo_id}")
def delete_todo(todo_id: uuid.UUID, session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    """ 刪除 todo - 檢查所有權 """
    todo = session.get(Todo, todo_id)
    if not todo:
        raise todo_not_found(str(todo_id))
    
    # 檢查所有權:用戶只能刪除自己的todo
    if todo.user_id != current_user.id:
        raise todo_access_denied(str(todo_id),current_user.id) 

    try:
        session.delete(todo)
        session.commit()
        return {"msg": "Todo deleted successfully","deleted_by": current_user.username}
    except Exception as e:
        session.rollback()
        raise NotFoundError(resource="Todo 刪除",details={"todo_id": str(todo_id), "error": str(e)})
    

# ============ 管理員專用端點 =============

@router.get("/admin/all",response_model=list[TodoOutWithUser])
def admin_get_all_todos(session: Session = Depends(get_session),admin_user: User = Depends(required_admin)):
    """ 管理員查看所有用戶的 todos (包含用戶信息) """
    todos = session.exec(select(Todo)).all()
    
    # 為每個 todo 加載用戶信息
    result = []
    for todo in todos:
        user = session.get(User,todo.user_id)
        # 使用 SimpleUserInfo 來避免循環引用
        simple_user = SimpleUserInfo(id=user.id,username=user.username,email=user.email) if user else None
        todo_with_user = TodoOutWithUser(**todo.model_dump(),user=simple_user)
        result.append(todo_with_user)
    return result

@router.get("/admin/user/{user_id}",response_model=list[TodoOutWithUser])
def admin_get_user_todos(user_id:int, session: Session = Depends(get_session),admin_user: User = Depends(required_admin)):
    """ 管理員查看特定用戶的所有 todos """
    user = session.get(User,user_id)
    if not user:
        raise NotFoundError(resource="用戶", details={"user_id":user_id}) 
    
    
    todos = session.exec(select(Todo).where(Todo.user_id == user_id)).all()
    return todos

@router.delete("/admin/{todo_id}")
def admin_delete_todo(todo_id:uuid.UUID,session: Session = Depends(get_session),admin_user: User = Depends(required_admin)):
    """ 管理員刪除任意 todo """
    todo = session.get(Todo,todo_id)
    if not todo:
        raise todo_not_found(str(todo_id))

    try:
        session.delete(todo)
        session.commit()
        return {"msg": f"管理員 {admin_user.username} 已刪除 todo {todo_id}" }
    except Exception as e:
        session.rollback()
        raise NotFoundError(resource="管理員 Todo 刪除",details={"todo_id": str(todo_id), "admin":admin_user.username,"error": str(e)})

