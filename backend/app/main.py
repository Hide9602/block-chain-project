"""
MetaSleuth NextGen - Backend Application
メインアプリケーションエントリーポイント
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, graph, report, analysis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    アプリケーションライフサイクル管理
    起動時と終了時の処理を定義
    """
    # 起動時処理
    logger.info("🚀 Starting MetaSleuth NextGen API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Version: {settings.API_VERSION}")
    
    # データベーステーブル作成（開発環境のみ）
    if settings.ENVIRONMENT == "development":
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    yield
    
    # 終了時処理
    logger.info("🛑 Shutting down MetaSleuth NextGen API...")
    await engine.dispose()
    logger.info("Database connections closed")


# FastAPI アプリケーション初期化
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="次世代ブロックチェーン調査プラットフォーム / Next-Generation Blockchain Investigation Platform",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS ミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP 圧縮ミドルウェア
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ヘルスチェックエンドポイント
@app.get("/health", tags=["Health"])
async def health_check():
    """
    ヘルスチェックエンドポイント
    
    Returns:
        dict: システムステータス
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    """
    ルートエンドポイント
    
    Returns:
        dict: API情報
    """
    return {
        "message": "Welcome to MetaSleuth NextGen API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "version": settings.API_VERSION,
    }


# API v1 ルーター登録
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"],
)

app.include_router(
    graph.router,
    prefix=f"{settings.API_V1_PREFIX}/graph",
    tags=["Graph Analysis"],
)

app.include_router(
    report.router,
    prefix=f"{settings.API_V1_PREFIX}/report",
    tags=["Report Generation"],
)

app.include_router(
    analysis.router,
    prefix=f"{settings.API_V1_PREFIX}/analysis",
    tags=["AI Analysis"],
)


# グローバルエラーハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    グローバル例外ハンドラー
    
    Args:
        request: FastAPI Request
        exc: 発生した例外
    
    Returns:
        JSONResponse: エラーレスポンス
    """
    logger.error(f"Unhandled exception: {exc}")
    logger.exception(exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.ENVIRONMENT == "development" else "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
