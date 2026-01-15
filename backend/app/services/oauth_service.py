"""Google OAuth 2.0 服務"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from urllib.parse import urlencode

import httpx
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.config import settings

logger = logging.getLogger(__name__)

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class OAuthService:
    """Google OAuth 2.0 服務"""

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.scopes = settings.GOOGLE_OAUTH_SCOPES

    @property
    def redirect_uri(self) -> str:
        """
        動態產生 redirect_uri

        優先使用 FRONTEND_URL + GOOGLE_OAUTH_CALLBACK_PATH，
        若 GOOGLE_REDIRECT_URI 有設定則使用舊設定（相容性）
        """
        if settings.GOOGLE_REDIRECT_URI:
            return settings.GOOGLE_REDIRECT_URI
        return f"{settings.FRONTEND_URL}{settings.GOOGLE_OAUTH_CALLBACK_PATH}"

    def generate_state(self) -> str:
        """產生 CSRF state 參數"""
        return secrets.token_urlsafe(32)

    def get_authorization_url(self, state: str) -> str:
        """
        取得 Google OAuth 授權 URL

        Args:
            state: CSRF 防護用的 state 參數

        Returns:
            Google OAuth 授權頁面 URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",  # 取得 refresh_token
            "prompt": "consent",  # 強制顯示同意畫面以取得 refresh_token
        }
        logger.info(f"OAuth redirect_uri: {self.redirect_uri}")
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_tokens(
        self, code: str
    ) -> Tuple[str, Optional[str], datetime]:
        """
        用授權碼交換 Access Token 和 Refresh Token

        Args:
            code: Google 回傳的授權碼

        Returns:
            (access_token, refresh_token, expires_at)
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            )

            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                raise ValueError(f"Token exchange failed: {response.text}")

            data = response.json()
            access_token = data["access_token"]
            refresh_token = data.get("refresh_token")  # 首次登入才有
            expires_in = data.get("expires_in", 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            logger.info("Successfully exchanged code for tokens")
            return access_token, refresh_token, expires_at

    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, datetime]:
        """
        使用 Refresh Token 取得新的 Access Token

        Args:
            refresh_token: Google Refresh Token

        Returns:
            (new_access_token, expires_at)
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.text}")
                raise ValueError(f"Token refresh failed: {response.text}")

            data = response.json()
            access_token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            logger.info("Successfully refreshed access token")
            return access_token, expires_at

    async def get_user_info(self, access_token: str) -> dict:
        """
        使用 Access Token 取得用戶資訊

        Args:
            access_token: Google Access Token

        Returns:
            用戶資訊 dict，包含 id, email, name, picture
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                logger.error(f"Get user info failed: {response.text}")
                raise ValueError(f"Get user info failed: {response.text}")

            data = response.json()
            logger.info(f"Got user info for: {data.get('email')}")
            return {
                "id": data["id"],
                "email": data["email"],
                "name": data.get("name", ""),
                "picture": data.get("picture"),
            }

    async def revoke_token(self, token: str) -> bool:
        """
        撤銷 Token（登出時可選用）

        Args:
            token: Access Token 或 Refresh Token

        Returns:
            是否成功撤銷
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/revoke",
                params={"token": token},
            )

            if response.status_code == 200:
                logger.info("Token revoked successfully")
                return True
            else:
                logger.warning(f"Token revocation failed: {response.text}")
                return False

    def get_credentials(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Credentials:
        """
        建立 Google Credentials 物件（用於 Google API）

        Args:
            access_token: Google Access Token
            refresh_token: Google Refresh Token
            expires_at: Token 過期時間

        Returns:
            google.oauth2.credentials.Credentials
        """
        return Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=GOOGLE_TOKEN_URL,
            client_id=self.client_id,
            client_secret=self.client_secret,
            expiry=expires_at,
        )


# 單例模式
oauth_service = OAuthService()
