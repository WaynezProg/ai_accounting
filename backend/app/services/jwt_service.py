"""JWT Token 服務"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import hashlib
import secrets

from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)


class JWTService:
    """JWT Token 管理服務"""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.expire_minutes = settings.JWT_ACCESS_EXPIRE_MINUTES or settings.JWT_EXPIRE_MINUTES

    def create_access_token(
        self,
        user_id: str,
        email: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        建立 JWT Access Token

        Args:
            user_id: 用戶 ID（Google User ID）
            email: 用戶 Email
            expires_delta: 自訂過期時間，預設使用設定值

        Returns:
            JWT Token 字串
        """
        expire = self._get_access_expiry(expires_delta)
        return self._encode_access_token(user_id=user_id, email=email, expire=expire)

    def create_access_token_with_expiry(
        self,
        user_id: str,
        email: str,
        expires_delta: Optional[timedelta] = None,
    ) -> tuple[str, datetime]:
        """
        建立 JWT Access Token 並回傳過期時間

        Args:
            user_id: 用戶 ID（Google User ID）
            email: 用戶 Email
            expires_delta: 自訂過期時間，預設使用設定值

        Returns:
            (JWT Token 字串, 過期時間)
        """
        expire = self._get_access_expiry(expires_delta)
        token = self._encode_access_token(user_id=user_id, email=email, expire=expire)
        return token, expire

    def create_refresh_token(self) -> str:
        """建立 Refresh Token（隨機字串）"""
        return secrets.token_urlsafe(48)

    def hash_refresh_token(self, token: str) -> str:
        """將 Refresh Token 進行 SHA256 雜湊"""
        return hashlib.sha256(token.encode()).hexdigest()

    def verify_token(self, token: str) -> Optional[dict]:
        """
        驗證 JWT Token

        Args:
            token: JWT Token 字串

        Returns:
            Token payload dict，驗證失敗回傳 None
        """
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )

            # 檢查是否為 access token
            if payload.get("type") != "access":
                logger.warning("Invalid token type")
                return None

            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        從 Token 取得用戶 ID

        Args:
            token: JWT Token 字串

        Returns:
            用戶 ID，驗證失敗回傳 None
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None

    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """
        取得 Token 過期時間

        Args:
            token: JWT Token 字串

        Returns:
            過期時間，驗證失敗回傳 None
        """
        payload = self.verify_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None

    def _get_access_expiry(self, expires_delta: Optional[timedelta]) -> datetime:
        if expires_delta:
            return datetime.utcnow() + expires_delta
        return datetime.utcnow() + timedelta(minutes=self.expire_minutes)

    def _encode_access_token(self, user_id: str, email: str, expire: datetime) -> str:
        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        logger.debug(f"Created JWT for user: {email}")
        return encoded_jwt


# 單例模式
jwt_service = JWTService()
