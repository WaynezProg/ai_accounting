"""認證相關工具"""

import logging
from typing import Optional

from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.token import token_store

logger = logging.getLogger(__name__)

# HTTP Bearer 安全方案
security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> bool:
    """
    驗證 Bearer Token

    用於需要認證的 API 端點

    Args:
        credentials: HTTP Authorization header

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

    if not token_store.verify_token(token):
        logger.warning(f"Invalid token attempt: {token[:8]}...")
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_TOKEN",
                "message": "無效的 Token",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Token verified: {token[:8]}...")
    return True


async def optional_verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[bool]:
    """
    可選的 Token 驗證

    用於同時支援認證和非認證請求的端點

    Args:
        credentials: HTTP Authorization header

    Returns:
        Optional[bool]: Token 是否有效，如果沒有提供則為 None
    """
    if credentials is None:
        return None

    token = credentials.credentials
    return token_store.verify_token(token)
