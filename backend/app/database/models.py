"""資料庫模型定義"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


class User(Base):
    """用戶資料表"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)  # Google User ID
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    picture: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
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
    sheet: Mapped[Optional["UserSheet"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class GoogleToken(Base):
    """Google OAuth Token 資料表"""
    __tablename__ = "google_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    access_token: Mapped[str] = mapped_column(Text, nullable=False)  # 加密儲存
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 加密儲存
    token_type: Mapped[str] = mapped_column(String(50), default="Bearer", nullable=False)
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
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)  # SHA256 hash
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


class UserSheet(Base):
    """用戶 Google Sheet 資料表"""
    __tablename__ = "user_sheets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    sheet_id: Mapped[str] = mapped_column(String(255), nullable=False)  # Google Sheet ID
    sheet_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sheet_name: Mapped[str] = mapped_column(String(255), default="記帳紀錄", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # 關聯
    user: Mapped["User"] = relationship(back_populates="sheet")
