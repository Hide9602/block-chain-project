"""
Configuration settings for MetaSleuth NextGen Backend
環境変数ベースの設定管理
"""

from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    アプリケーション設定クラス
    環境変数から自動的に値を読み込む
    """
    
    # プロジェクト情報
    PROJECT_NAME: str = "MetaSleuth NextGen API"
    API_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # セキュリティ
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS設定
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://metasleuth-nextgen.com",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # データベース設定
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "metasleuth"
    POSTGRES_PASSWORD: str = "metasleuth_password"
    POSTGRES_DB: str = "metasleuth_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Neo4j設定
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_password"
    
    # Redis設定
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ブロックチェーンAPI設定
    ETHERSCAN_API_KEY: Optional[str] = None
    INFURA_PROJECT_ID: Optional[str] = None
    ALCHEMY_API_KEY: Optional[str] = None
    
    # Celery設定
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @property
    def CELERY_BROKER(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL
    
    @property
    def CELERY_BACKEND(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL
    
    # ファイルストレージ設定
    UPLOAD_DIR: str = "/tmp/metasleuth/uploads"
    REPORTS_DIR: str = "/tmp/metasleuth/reports"  # Changed from REPORT_DIR for consistency
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # レポート生成設定
    REPORT_TIMEOUT_SECONDS: int = 300  # 5分
    REPORT_MAX_NODES: int = 10000
    REPORT_MAX_HOPS: int = 10
    
    # レート制限設定
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ログ設定
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # メール設定（将来の機能用）
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    
    # 機械学習設定
    ML_MODEL_PATH: str = "/app/models"
    ML_DEVICE: str = "cpu"  # cpu, cuda, mps
    ML_BATCH_SIZE: int = 32
    
    # パターン認識設定
    PATTERN_CONFIDENCE_THRESHOLD: float = 0.8
    RISK_SCORE_THRESHOLD_HIGH: int = 80
    RISK_SCORE_THRESHOLD_MEDIUM: int = 50
    
    # 監視設定
    ENABLE_PROMETHEUS: bool = True
    PROMETHEUS_PORT: int = 9090
    
    # デバッグ設定
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# グローバル設定インスタンス
settings = Settings()
