"""
Database configuration and session management
データベース設定とセッション管理
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from neo4j import AsyncGraphDatabase
from redis.asyncio import Redis

from app.core.config import settings

# SQLAlchemy (PostgreSQL)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    データベースセッションのDependency
    
    Yields:
        AsyncSession: データベースセッション
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Neo4j Graph Database
class Neo4jDatabase:
    """Neo4j グラフデータベースクライアント"""
    
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    async def close(self):
        """ドライバーのクローズ"""
        await self.driver.close()
    
    async def verify_connectivity(self):
        """接続確認"""
        await self.driver.verify_connectivity()
    
    async def execute_query(self, query: str, parameters: dict = None):
        """
        Cypherクエリの実行
        
        Args:
            query: Cypherクエリ
            parameters: クエリパラメータ
        
        Returns:
            クエリ結果
        """
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            return await result.data()


neo4j_db = Neo4jDatabase()


async def get_neo4j() -> Neo4jDatabase:
    """
    Neo4jデータベースのDependency
    
    Returns:
        Neo4jDatabase: Neo4jクライアント
    """
    return neo4j_db


# Redis Cache
redis_client = Redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> Redis:
    """
    Redisクライアントの Dependency
    
    Returns:
        Redis: Redisクライアント
    """
    return redis_client


async def init_db():
    """
    データベースの初期化
    開発環境でのみテーブル作成
    """
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    データベース接続のクローズ
    """
    await engine.dispose()
    await neo4j_db.close()
    await redis_client.close()
