"""
Security utilities for authentication and authorization
認証・認可のためのセキュリティユーティリティ
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

# パスワードハッシュ化コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT認証スキーム
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    平文パスワードとハッシュ化パスワードの検証
    
    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化パスワード
    
    Returns:
        bool: 一致する場合True
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードのハッシュ化
    
    Args:
        password: 平文パスワード
    
    Returns:
        str: ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    アクセストークンの生成
    
    Args:
        data: トークンに含めるデータ
        expires_delta: 有効期限（デフォルト: 30分）
    
    Returns:
        str: JWTトークン
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    リフレッシュトークンの生成
    
    Args:
        data: トークンに含めるデータ
    
    Returns:
        str: JWTトークン
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    JWTトークンのデコード
    
    Args:
        token: JWTトークン
    
    Returns:
        dict: デコードされたペイロード
    
    Raises:
        HTTPException: トークンが無効な場合
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    現在のユーザー情報を取得（Dependency）
    
    Args:
        credentials: HTTPAuthorizationCredentials
    
    Returns:
        dict: ユーザー情報
    
    Raises:
        HTTPException: 認証失敗時
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    # トークンタイプの確認
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "email": payload.get("email")}


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    アクティブなユーザーのみを許可（Dependency）
    
    Args:
        current_user: 現在のユーザー
    
    Returns:
        dict: ユーザー情報
    
    Raises:
        HTTPException: ユーザーが非アクティブな場合
    """
    # TODO: データベースからユーザー情報を取得し、is_activeをチェック
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


def check_permissions(required_permissions: list[str]):
    """
    権限チェックのデコレータ
    
    Args:
        required_permissions: 必要な権限のリスト
    
    Returns:
        Dependency関数
    """
    async def permission_checker(
        current_user: dict = Depends(get_current_active_user)
    ):
        # TODO: ユーザーの権限をチェック
        # user_permissions = get_user_permissions(current_user["user_id"])
        # if not all(perm in user_permissions for perm in required_permissions):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Not enough permissions"
        #     )
        return current_user
    
    return permission_checker
