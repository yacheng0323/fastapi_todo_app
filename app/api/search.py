# 分頁
import select
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.sql import or_,func
from sqlmodel import Session, select
from app.api.todo import router
from app.deps.users import get_current_user
from app.models.user import User
from app.models.todo import PaginatedTodoResponse, Todo, TodoSortBy
from app.db.session import get_session

router = APIRouter()


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