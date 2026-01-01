"""資料庫引擎設定

支援兩種資料庫模式：
1. Turso (生產環境)：使用 libsql-sqlalchemy
2. SQLite (本地開發)：使用標準 sqlite

統一使用同步 Session 以簡化程式碼。
"""

import logging
import os
from typing import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy 基礎類別"""
    pass


def is_turso_enabled() -> bool:
    """檢查是否啟用 Turso"""
    turso_url = os.getenv("TURSO_DATABASE_URL")
    turso_token = os.getenv("TURSO_AUTH_TOKEN")
    return bool(turso_url and turso_token)


def get_turso_config() -> tuple[str, str]:
    """取得 Turso 設定"""
    turso_url = os.getenv("TURSO_DATABASE_URL", "")
    turso_token = os.getenv("TURSO_AUTH_TOKEN", "")
    # 移除 libsql:// 前綴，因為 libsql-sqlalchemy 格式是 sqlite+libsql://host
    host = turso_url.replace("libsql://", "")
    return host, turso_token


def get_sqlite_url() -> str:
    """取得本地 SQLite URL"""
    DATABASE_DIR = Path(__file__).parent.parent.parent / "data"
    DATABASE_DIR.mkdir(exist_ok=True)
    return f"sqlite:///{DATABASE_DIR}/app.db"


# 判斷使用哪種資料庫
USE_TURSO = is_turso_enabled()

if USE_TURSO:
    # Turso：使用 libsql-sqlalchemy
    turso_host, turso_token = get_turso_config()
    DATABASE_URL = f"sqlite+libsql://{turso_host}?secure=true"
    logger.info(f"Using Turso database: {turso_host}")

    engine = create_engine(
        DATABASE_URL,
        echo=settings.ENV == "development",
        connect_args={"auth_token": turso_token},
    )
else:
    # 本地開發：使用同步 SQLite
    DATABASE_URL = get_sqlite_url()
    logger.info(f"Using local SQLite database: {DATABASE_URL}")

    engine = create_engine(
        DATABASE_URL,
        echo=settings.ENV == "development",
        connect_args={"check_same_thread": False},
    )

# 統一使用同步 Session 工廠
SessionLocal = sessionmaker(
    engine,
    class_=Session,
    expire_on_commit=False,
)


def init_db() -> None:
    """初始化資料庫（建立表格）"""
    # 導入模型以確保它們被註冊
    from app.database import models  # noqa: F401

    Base.metadata.create_all(engine)
    logger.info("Database initialized")


def close_db() -> None:
    """關閉資料庫連線"""
    engine.dispose()
    logger.info("Database connection closed")


def get_db() -> Generator[Session, None, None]:
    """取得資料庫 Session（用於 FastAPI Depends）"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
