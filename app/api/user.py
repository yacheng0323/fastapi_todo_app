from fastapi import APIRouter, FastAPI, Depends, Form, HTTPException, status
from sqlmodel import SQLModel, Session, select
from app.models.user import User, UserCreate, UserOut
from app.db.session import get_session
from app.core.security import (
    create_refresh_token,
    verify_password,
    create_access_token,
    get_password_hash,
    decode_refresh_token,
)
from app.deps.users import get_current_user

from app.core.exceptions import (
    user_already_exists,
    invalid_credentials,
    NotFoundError,
    AuthenticationError,
    ValidationError,
)

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    """用戶註冊端點"""
    try:
        # 先檢查帳號是否存在
        existing_user = session.exec(
            select(User).where(User.username == user_in.username)
        ).first()
        if existing_user:
            raise user_already_exists(user_in.username)

        # 檢查email是否存在
        if user_in.email:
            existing_email = session.exec(
                select(User).where(User.email == user_in.email)
            ).first()
            if existing_email:
                raise user_already_exists(user_in.email)

        user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except (ValidationError, AuthenticationError) as e:
        # 重新丟出我們的自定義錯誤
        session.rollback()
        raise e
    except Exception as e:
        # 處理資料庫或其他錯誤
        session.rollback()
        raise ValidationError(
            message="用戶註冊失敗",
            details={"error": str(e), "username": user_in.username},
        )


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    """用戶登入端點"""
    try:
        # 查找使用者
        user = session.exec(select(User).where(User.username == username)).first()

        # 驗證用戶存在性和密碼
        if not user or not verify_password(password, user.hashed_password):
            # 使用統一錯誤處理
            raise invalid_credentials()

        # 建立 token
        access_token = create_access_token(
            {"sub": str(user.id), "role": user.role.value}
        )
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
            },
        }

    except (AuthenticationError, ValidationError) as e:
        # 重新丟出我們的自定義錯誤
        raise e
    except Exception as e:
        # 處理其他未預期錯誤
        raise AuthenticationError(
            message="登入處理失敗", details={"error": str(e), "username": username}
        )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """獲取當前用戶的資訊"""
    return current_user


@router.post("/refresh")
def refresh_token(
    refresh_token: str = Form(...), session: Session = Depends(get_session)
):
    """刷新存取令牌"""
    try:
        # 解碼 refresh token
        payload = decode_refresh_token(refresh_token)
        if payload is None:
            # 使用統一錯誤處理
            raise AuthenticationError(
                message="無效的token", details={"token_type": "refresh_token"}
            )

        # 獲取用戶 ID
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError(
                message="令牌中缺少用戶 ID", details={"token_type": "refresh_token"}
            )

        user = session.get(User, int(user_id))
        if not user:
            raise NotFoundError(
                resource="用戶", details={"user_id": user_id, "source": "refresh_token"}
            )

        # 創建新的存取令牌
        new_access_token = create_access_token(
            {"sub": str(user.id), "role": user.role.value}
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
            },
        }

    except (AuthenticationError, NotFoundError, ValidationError) as e:
        # 重新丟出我們的自定義錯誤
        raise e
    except ValueError as e:
        # 處理 user_id 轉換錯誤
        raise AuthenticationError(
            message="令牌中的用戶 ID 格式無效", details={"error": str(e)}
        )
    except Exception as e:
        # 處理其他未預期錯誤
        raise AuthenticationError(message="令牌刷新失敗", details={"error": str(e)})


# 新增:用戶管理端點 (管理員用)
@router.get("/admin/users", response_model=list[UserOut])
def get_all_users(
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """管理員獲取所有用戶列表"""
    if admin_user.role.value != "admin":
        raise AuthenticationError(
            message="需要管理員權限",
            details={"required_role": "admin", "current_role": admin_user.role.value},
        )

    try:
        users = session.exec(select(User)).all()
        return users
    except Exception as e:
        raise NotFoundError(resource="用戶列表", details={"error": str(e)})


@router.get("/admin/users/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: int,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_user),
):
    """管理員通過 ID 獲取用戶"""
    # 檢查管理員權限
    if admin_user.role.value != "admin":
        raise AuthenticationError(
            message="需要管理員權限",
            details={"required_role": "admin", "current_role": admin_user.role.value},
        )

    user = session.get(User, user_id)
    if not user:
        raise NotFoundError(
            resource="用戶",
            details={"user_id": user_id, "requested_by": admin_user.username},
        )
    return user


@router.get("/test-error/{error_type}")
def test_error_handing(error_type: str):
    """測試不同類型的錯誤處理"""
    if error_type == "not_found":
        raise NotFoundError(resource="測試資源")
    elif error_type == "auth":
        raise AuthenticationError(message="測試認證錯誤")
    elif error_type == "validation":
        raise ValidationError(
            message="測試資料驗證錯誤", details={"field": "test_field"}
        )
    elif error_type == "general":
        raise Exception("這是一個測試用的一般例外")
    else:
        return {
            "message": f"未知的錯誤類型: {error_type}",
            "available_types": ["not_found", "auth", "validation", "general"],
        }
