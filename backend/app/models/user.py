"""
User Model
ユーザーモデル
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class User(Base):
    """ユーザーモデル"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # ステータス
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # ロール
    role = Column(String(50), default="user", nullable=False)  # user, admin, investigator
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # プロフィール
    organization = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    
    # 設定
    language = Column(String(10), default="ja", nullable=False)
    timezone = Column(String(50), default="Asia/Tokyo", nullable=False)
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
    
    @property
    def is_admin(self) -> bool:
        """管理者かどうか"""
        return self.is_superuser or self.role == "admin"
