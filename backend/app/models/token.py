"""Token 資料模型"""

import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field

from app.config import settings


class APIToken(BaseModel):
    """API Token 資料"""

    token: str = Field(..., description="Token 值")
    description: str = Field(default="", description="Token 描述，如 'Siri 捷徑'")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=None, description="過期時間，None 表示永不過期")
    is_active: bool = Field(default=True)

    def is_valid(self) -> bool:
        """檢查 Token 是否有效"""
        if not self.is_active:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True


class TokenStore:
    """
    Token 儲存（簡易版，使用 JSON 檔案）

    Phase 5 會改為使用 SQLite/Cloud SQL
    """

    def __init__(self, file_path: str = None):
        self.file_path = file_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "tokens.json",
        )
        self._ensure_file()

    def _ensure_file(self):
        """確保檔案和目錄存在"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def _load_tokens(self) -> List[dict]:
        """載入所有 Token"""
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_tokens(self, tokens: List[dict]):
        """儲存 Token"""
        with open(self.file_path, "w") as f:
            json.dump(tokens, f, default=str, indent=2)

    def generate_token(
        self,
        description: str = "",
        expires_in_days: Optional[int] = None,
    ) -> APIToken:
        """
        生成新的 API Token

        Args:
            description: Token 描述
            expires_in_days: 幾天後過期，None 表示永不過期

        Returns:
            APIToken: 新建立的 Token
        """
        token_value = secrets.token_urlsafe(32)

        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        api_token = APIToken(
            token=token_value,
            description=description,
            created_at=datetime.now(),
            expires_at=expires_at,
            is_active=True,
        )

        # 儲存
        tokens = self._load_tokens()
        tokens.append(api_token.model_dump())
        self._save_tokens(tokens)

        return api_token

    def verify_token(self, token: str) -> bool:
        """
        驗證 Token 是否有效

        Args:
            token: Token 值

        Returns:
            bool: 是否有效
        """
        tokens = self._load_tokens()
        for t in tokens:
            if t["token"] == token:
                api_token = APIToken(**t)
                return api_token.is_valid()
        return False

    def get_token(self, token: str) -> Optional[APIToken]:
        """
        取得 Token 資訊

        Args:
            token: Token 值

        Returns:
            APIToken: Token 資訊，如果不存在則回傳 None
        """
        tokens = self._load_tokens()
        for t in tokens:
            if t["token"] == token:
                return APIToken(**t)
        return None

    def revoke_token(self, token: str) -> bool:
        """
        撤銷 Token

        Args:
            token: Token 值

        Returns:
            bool: 是否成功
        """
        tokens = self._load_tokens()
        for t in tokens:
            if t["token"] == token:
                t["is_active"] = False
                self._save_tokens(tokens)
                return True
        return False

    def list_tokens(self, include_inactive: bool = False) -> List[APIToken]:
        """
        列出所有 Token

        Args:
            include_inactive: 是否包含已撤銷的 Token

        Returns:
            List[APIToken]: Token 列表
        """
        tokens = self._load_tokens()
        result = []
        for t in tokens:
            api_token = APIToken(**t)
            if include_inactive or api_token.is_active:
                result.append(api_token)
        return result


# 單例模式
token_store = TokenStore()
