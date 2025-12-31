"""資料庫引擎設定"""

import logging
from typing import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy 基礎類別"""
    pass


# 資料庫檔案路徑
DATABASE_DIR = Path(__file__).parent.parent.parent / "data"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_DIR}/app.db"

# 建立引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.ENV == "development",
)

# 建立 Session 工廠
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """初始化資料庫（建立表格）"""
    # 導入模型以確保它們被註冊
    from app.database import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized")


async def close_db() -> None:
    """關閉資料庫連線"""
    await engine.dispose()
    logger.info("Database connection closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """取得資料庫 Session（用於 FastAPI Depends）"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
