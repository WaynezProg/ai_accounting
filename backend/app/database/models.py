"""資料庫模型定義"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


class User(Base):
    """用戶資料表"""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)  # Google User ID
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    picture: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, default="Asia/Taipei"
    )  # IANA timezone name (e.g., "Asia/Taipei", "America/New_York")
    monthly_budget: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None
    )  # 月預算金額（整數，單位：TWD）
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 關聯
    google_token: Mapped[Optional["GoogleToken"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    api_tokens: Mapped[list["APIToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    refresh_token: Mapped[Optional["RefreshToken"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    oauth_login_codes: Mapped[list["OAuthLoginCode"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    sheet: Mapped[Optional["UserSheet"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    query_history: Mapped[list["QueryHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class GoogleToken(Base):
    """Google OAuth Token 資料表"""

    __tablename__ = "google_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    access_token: Mapped[str] = mapped_column(Text, nullable=False)  # 加密儲存
    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # 加密儲存
    token_type: Mapped[str] = mapped_column(
        String(50), default="Bearer", nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scope: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 關聯
    user: Mapped["User"] = relationship(back_populates="google_token")


class APIToken(Base):
    """API Token 資料表（取代原本的 JSON 儲存）"""

    __tablename__ = "api_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )  # SHA256 hash
    user_id: Mapped[Optional[str]] = mapped_column(
        String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )  # 可為 null（相容舊版無用戶的 Token）
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 關聯
    user: Mapped[Optional["User"]] = relationship(back_populates="api_tokens")


class RefreshToken(Base):
    """JWT Refresh Token 資料表"""

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="refresh_token")


class OAuthLoginCode(Base):
    """OAuth 回調 one-time code 資料表"""

    __tablename__ = "oauth_login_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    code_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="oauth_login_codes")


class UserSheet(Base):
    """用戶 Google Sheet 資料表"""

    __tablename__ = "user_sheets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    sheet_id: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Google Sheet ID
    sheet_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sheet_name: Mapped[str] = mapped_column(
        String(255), default="記帳紀錄", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # 關聯
    user: Mapped["User"] = relationship(back_populates="sheet")


class QueryHistory(Base):
    """查詢記錄資料表"""

    __tablename__ = "query_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)  # 使用者的問題
    answer: Mapped[str] = mapped_column(Text, nullable=False)  # AI 的回答
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # 關聯
    user: Mapped["User"] = relationship(back_populates="query_history")
