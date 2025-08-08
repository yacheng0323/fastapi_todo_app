import datetime
from typing import Optional
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlmodel import select
from app.deps.users import get_current_user, required_admin
from app.models.todo import SimpleUserInfo, Todo,TodoCreate,TodoOut, TodoOutWithUser,TodoUpdate, TodoSortBy, PaginatedTodoResponse
from app.db.session import get_session
from sqlmodel import Session
from sqlalchemy import func,or_
import uuid

from app.models.user import User

router = APIRouter()

@router.post("/",response_model=TodoOut)
def create_todo(todo: TodoCreate,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    """創建新的 todo - 自動關連到當前用戶"""
    db_todo = Todo(**todo.model_dump(),user_id=current_user.id)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@router.get("/",response_model=list[TodoOut])
def read_todos(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """ 獲取當前用戶的所有 todos - 用戶隔離 """
    todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    return todos

# 分頁
@router.get("/search",response_model=PaginatedTodoResponse)
def search_todos(
    q: Optional[str] = None,
    sort_by: TodoSortBy = TodoSortBy.created_at_desc,
    page: int = Query(1,ge=1),
    per_page: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 基本條件:僅限當前用戶
    conditions = [Todo.user_id == current_user.id]

    # 關鍵字搜尋 (title / description 都支援，忽略大小寫)
    if q: 
        pattern = f"%{q}%"
        conditions.append(or_(Todo.title.ilike(pattern),Todo.description.ilike(pattern)))

    # 組出查詢 (先不分頁)
    stmt = select(Todo).where(*conditions)

    # 排序對應
    order_by_map = {
        TodoSortBy.created_at_asc: Todo.created_at.asc(),
        TodoSortBy.created_at_desc: Todo.created_at.desc(),
        TodoSortBy.updated_at_asc: Todo.updated_at.asc(),
        TodoSortBy.updated_at_desc: Todo.updated_at.desc(),
        TodoSortBy.title_asc: Todo.title.asc(),
        TodoSortBy.title_desc: Todo.title.desc(),
    }
    stmt = stmt.order_by(order_by_map[sort_by])

    # 總筆數 (未分頁前)
    count_stmt = select(func.count()).select_from(Todo).where(*conditions)
    total = session.exec(count_stmt).one()

    # 分頁
    offset = (page - 1) * per_page
    items = session.exec(stmt.offset(offset).limit(per_page)).all()

    # 總頁數
    pages = (total + per_page - 1) // per_page if total else 0

    return PaginatedTodoResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )

@router.get("/{todo_id}",response_model=TodoOut)
def read_todo(todo_id: uuid.UUID,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    """ 獲取特定 todo - 檢查所有權 """
    todo = session.get(Todo,todo_id)
    if not todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    
    # 🛡️ 檢查所有權：用戶只能訪問自己的 todo
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403,detail="無權限訪問此 Todo")
    
    return todo

@router.put("/{todo_id}",response_model=TodoOut)
def update_todo(todo_id: uuid.UUID,updated_todo: TodoUpdate,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    """ 更新 todo - 檢查所有權並自動更新時間戳記 """
    todo = session.get(Todo,todo_id)
    if not todo:
        raise HTTPException(status_code=404,detail="Todo not found")

    # 檢查所有權:用戶只能更新自己的 todo
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403,detail="無權限更新此 Todo")

    # 更新字段
    for key,value in updated_todo.dict(exclude_unset=True).items():
        setattr(todo,key,value)

    todo.updated_at = datetime.datetime.now()

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.delete("/{todo_id}")
def delete_todo(todo_id: uuid.UUID, session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    """ 刪除 todo - 檢查所有權 """
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # 檢查所有權:用戶只能刪除自己的todo
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403,detail="無權限刪除此 Todo")
    
    session.delete(todo)
    session.commit()
    return {"msg": "Todo deleted successfully","deleted_by": current_user.username}

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
        raise HTTPException(status_code=404,detail="用戶不存在")
    
    todos = session.exec(select(Todo).where(Todo.user_id == user_id)).all()
    return todos

@router.delete("/admin/{todo_id}")
def admin_delete_todo(todo_id:uuid.UUID,session: Session = Depends(get_session),admin_user: User = Depends(required_admin)):
    """ 管理員刪除任意 todo """
    todo = session.get(Todo,todo_id)
    if not todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    
    session.delete(todo)
    session.commit()
    return {"msg": f"管理員 {admin_user.username} 已刪除 todo {todo_id}" }

