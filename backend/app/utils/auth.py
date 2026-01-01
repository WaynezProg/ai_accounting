"""認證相關工具"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.database.crud import verify_api_token, get_user_by_id
from app.services.jwt_service import jwt_service

logger = logging.getLogger(__name__)

# HTTP Bearer 安全方案
security = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[dict]:
    """
    取得當前用戶（可選）

    支援兩種認證方式：
    1. JWT Token（OAuth 登入用戶）
    2. API Token（Siri 捷徑等外部服務）

    Args:
        credentials: HTTP Authorization header
        db: 資料庫 Session

    Returns:
        用戶資訊 dict，包含 user_id, email, auth_type
        未認證則返回 None
    """
    if credentials is None:
        return None

    token = credentials.credentials

    # 1. 嘗試 JWT 驗證
    jwt_payload = jwt_service.verify_token(token)
    if jwt_payload:
        user_id = jwt_payload.get("sub")
        email = jwt_payload.get("email")
        logger.debug(f"JWT auth for user: {email}")
        return {
            "user_id": user_id,
            "email": email,
            "auth_type": "jwt",
        }

    # 2. 嘗試 API Token 驗證
    api_token = verify_api_token(db, token)
    if api_token:
        logger.debug(f"API Token auth, user_id: {api_token.user_id}")
        return {
            "user_id": api_token.user_id,
            "email": None,
            "auth_type": "api_token",
            "token_id": api_token.id,
        }

    # 兩種驗證都失敗
    return None


def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> bool:
    """
    驗證 Bearer Token（必要）

    用於需要認證的 API 端點
    支援 JWT 和 API Token

    Args:
        credentials: HTTP Authorization header
        db: 資料庫 Session

    Returns:
        bool: Token 是否有效

    Raises:
        HTTPException: 如果 Token 無效
    """
    if credentials is None:
        logger.warning("No authorization header provided")
        raise HTTPException(
            status_code=401,
            detail={
                "code": "NO_TOKEN",
                "message": "未提供認證 Token",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # 1. 嘗試 JWT 驗證
    jwt_payload = jwt_service.verify_token(token)
    if jwt_payload:
        logger.info(f"JWT verified for: {jwt_payload.get('email')}")
        return True

    # 2. 嘗試 API Token 驗證
    api_token = verify_api_token(db, token)
    if api_token:
        logger.info(f"API Token verified: {token[:8]}...")
        return True

    # 兩種驗證都失敗
    logger.warning(f"Invalid token attempt: {token[:8]}...")
    raise HTTPException(
        status_code=401,
        detail={
            "code": "INVALID_TOKEN",
            "message": "無效的 Token",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """
    取得當前用戶（必要）

    與 get_current_user_optional 類似，但未認證時會拋出例外

    Args:
        credentials: HTTP Authorization header
        db: 資料庫 Session

    Returns:
        用戶資訊 dict

    Raises:
        HTTPException: 如果未認證
    """
    user = get_current_user_optional(credentials, db)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "UNAUTHORIZED",
                "message": "需要登入",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def optional_verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[bool]:
    """
    可選的 Token 驗證

    用於同時支援認證和非認證請求的端點

    Args:
        credentials: HTTP Authorization header
        db: 資料庫 Session

    Returns:
        Optional[bool]: Token 是否有效，如果沒有提供則為 None
    """
    if credentials is None:
        return None

    token = credentials.credentials

    # 嘗試 JWT 驗證
    if jwt_service.verify_token(token):
        return True

    # 嘗試 API Token 驗證
    api_token = verify_api_token(db, token)
    return api_token is not None
