"""認證 API 端點"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.models.token import token_store, APIToken
from app.utils.auth import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()


# =========================
# 請求/回應模型
# =========================


class GenerateTokenRequest(BaseModel):
    """產生 Token 請求"""

    description: str = Field(default="Siri 捷徑", description="Token 描述")
    expires_in_days: Optional[int] = Field(
        default=None, description="幾天後過期，None 表示永不過期"
    )


class TokenResponse(BaseModel):
    """Token 回應"""

    success: bool = True
    token: str
    description: str
    created_at: str
    expires_at: Optional[str] = None
    message: str


class VerifyTokenResponse(BaseModel):
    """驗證 Token 回應"""

    success: bool = True
    valid: bool
    message: str


# =========================
# API 端點
# =========================


@router.post("/token/generate", response_model=TokenResponse)
async def generate_token(request: GenerateTokenRequest):
    """
    產生新的 API Token

    此 Token 用於 Siri 捷徑等外部服務呼叫 API

    注意：Phase 5 後此端點需要 OAuth 登入才能使用
    """
    logger.info(f"Generating token: {request.description}")

    api_token = token_store.generate_token(
        description=request.description,
        expires_in_days=request.expires_in_days,
    )

    return TokenResponse(
        success=True,
        token=api_token.token,
        description=api_token.description,
        created_at=api_token.created_at.isoformat(),
        expires_at=api_token.expires_at.isoformat() if api_token.expires_at else None,
        message="Token 已產生，請妥善保管",
    )


@router.get("/token/verify", response_model=VerifyTokenResponse)
async def verify_token_endpoint(token_valid: bool = Depends(verify_token)):
    """
    驗證 Token 是否有效

    需要在 Authorization header 提供 Bearer Token
    """
    return VerifyTokenResponse(
        success=True,
        valid=True,
        message="Token 有效",
    )


@router.get("/status")
async def get_auth_status(token_valid: bool = Depends(verify_token)):
    """
    檢查認證狀態

    需要在 Authorization header 提供 Bearer Token
    """
    return {
        "success": True,
        "authenticated": True,
        "auth_type": "api_token",
    }
