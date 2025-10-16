"""
Authentication API endpoints
認証関連のAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_token,
)

router = APIRouter()


# リクエスト/レスポンスモデル
class UserRegisterRequest(BaseModel):
    """ユーザー登録リクエスト"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """トークンレスポンス"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterRequest):
    """
    ユーザー登録
    
    Args:
        user_data: ユーザー登録データ
    
    Returns:
        UserResponse: 登録されたユーザー情報
    
    Raises:
        HTTPException: メールアドレスが既に登録されている場合
    """
    # TODO: データベースにユーザーが既に存在するかチェック
    # existing_user = await db.get_user_by_email(user_data.email)
    # if existing_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Email already registered"
    #     )
    
    # パスワードハッシュ化
    hashed_password = get_password_hash(user_data.password)
    
    # TODO: データベースに新規ユーザーを作成
    # new_user = await db.create_user(
    #     email=user_data.email,
    #     hashed_password=hashed_password,
    #     full_name=user_data.full_name
    # )
    
    # 仮のレスポンス
    return UserResponse(
        id="user-001",
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLoginRequest):
    """
    ログイン
    
    Args:
        credentials: ログイン情報
    
    Returns:
        TokenResponse: アクセストークンとリフレッシュトークン
    
    Raises:
        HTTPException: 認証失敗時
    """
    # TODO: データベースからユーザーを取得
    # user = await db.get_user_by_email(credentials.email)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect email or password"
    #     )
    
    # TODO: パスワード検証
    # if not verify_password(credentials.password, user.hashed_password):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect email or password"
    #     )
    
    # トークン生成（仮のユーザーID）
    user_id = "user-001"
    access_token = create_access_token(data={"sub": user_id, "email": credentials.email})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """
    トークンリフレッシュ
    
    Args:
        refresh_token: リフレッシュトークン
    
    Returns:
        TokenResponse: 新しいアクセストークンとリフレッシュトークン
    
    Raises:
        HTTPException: トークンが無効な場合
    """
    try:
        payload = decode_token(refresh_token)
        
        # トークンタイプの確認
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        # 新しいトークン生成
        new_access_token = create_access_token(data={"sub": user_id, "email": email})
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) from e


@router.get("/me", response_model=UserResponse)
async def get_current_user_info():
    """
    現在のユーザー情報取得
    
    Returns:
        UserResponse: ユーザー情報
    """
    # TODO: get_current_user Dependencyから取得
    # user = Depends(get_current_active_user)
    
    # 仮のレスポンス
    return UserResponse(
        id="user-001",
        email="user@example.com",
        full_name="Test User",
        is_active=True
    )
