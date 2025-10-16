"""
Authentication API endpoints
認証関連のAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_token,
    get_current_user,
)
from app.core.database import get_db
from app.crud.user import user_crud
from app.models.user import User

logger = logging.getLogger(__name__)

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
async def register(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    ユーザー登録
    
    Args:
        user_data: ユーザー登録データ
        db: Database session
    
    Returns:
        UserResponse: 登録されたユーザー情報
    
    Raises:
        HTTPException: メールアドレスが既に登録されている場合
    """
    try:
        # Check if user already exists
        existing_user = await user_crud.get_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = await user_crud.create(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        logger.info(f"New user registered: {new_user.email}")
        
        return UserResponse(
            id=str(new_user.id),
            email=new_user.email,
            full_name=new_user.full_name,
            is_active=new_user.is_active
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    ログイン
    
    Args:
        credentials: ログイン情報
        db: Database session
    
    Returns:
        TokenResponse: アクセストークンとリフレッシュトークン
    
    Raises:
        HTTPException: 認証失敗時
    """
    try:
        # Get user from database
        user = await user_crud.get_by_email(db, credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        # Update last login timestamp
        await user_crud.update_last_login(db, str(user.id))
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
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
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    現在のユーザー情報取得
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        UserResponse: ユーザー情報
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active
    )
