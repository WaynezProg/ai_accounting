"""認證 API 端點"""

import logging
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Response, Cookie
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.database.crud import (
    get_or_create_user,
    save_google_token,
    get_google_token,
    create_api_token,
    get_user_api_tokens,
    revoke_api_token,
    get_user_by_id,
)
from app.services.oauth_service import oauth_service
from app.services.jwt_service import jwt_service
from app.utils.auth import verify_token, get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter()

# 暫存 OAuth state（生產環境應使用 Redis）
oauth_states: dict[str, bool] = {}


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


class UserInfo(BaseModel):
    """用戶資訊"""

    id: str
    email: str
    name: str
    picture: Optional[str] = None


class MeResponse(BaseModel):
    """當前用戶回應"""

    success: bool = True
    user: UserInfo
    auth_type: str


class APITokenInfo(BaseModel):
    """API Token 資訊"""

    id: int
    description: str
    created_at: str
    expires_at: Optional[str] = None
    last_used_at: Optional[str] = None
    is_active: bool


class APITokenListResponse(BaseModel):
    """API Token 列表回應"""

    success: bool = True
    tokens: list[APITokenInfo]


# =========================
# Google OAuth 端點
# =========================


@router.get("/google/login")
async def google_login():
    """
    開始 Google OAuth 登入流程

    重導向至 Google 授權頁面
    """
    state = oauth_service.generate_state()
    oauth_states[state] = True  # 記錄有效 state

    auth_url = oauth_service.get_authorization_url(state)
    logger.info(f"Redirecting to Google OAuth, state: {state[:8]}...")
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Google 授權碼"),
    state: str = Query(..., description="CSRF state 參數"),
    db: Session = Depends(get_db),
):
    """
    Google OAuth 回調端點

    處理 Google 授權後的回調，建立用戶並發放 JWT
    """
    # 1. 驗證 state
    if state not in oauth_states:
        logger.warning(f"Invalid OAuth state: {state[:8]}...")
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    del oauth_states[state]

    try:
        # 2. 交換授權碼為 Token
        access_token, refresh_token, expires_at = (
            await oauth_service.exchange_code_for_tokens(code)
        )

        # 3. 取得用戶資訊
        user_info = await oauth_service.get_user_info(access_token)

        # 4. 建立或更新用戶
        user, is_new = get_or_create_user(
            db,
            user_id=user_info["id"],
            email=user_info["email"],
            name=user_info["name"],
            picture=user_info.get("picture"),
        )

        # 5. 儲存 Google Token
        save_google_token(
            db,
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scope=" ".join(settings.GOOGLE_OAUTH_SCOPES),
        )

        # 6. 建立 JWT
        jwt_token = jwt_service.create_access_token(
            user_id=user.id,
            email=user.email,
        )

        # 7. 重導向至前端，帶上 JWT
        params = {
            "token": jwt_token,
            "new_user": "1" if is_new else "0",
        }
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?{urlencode(params)}"

        logger.info(f"OAuth success for user: {user.email}, new: {is_new}")
        return RedirectResponse(url=redirect_url)

    except ValueError as e:
        logger.error(f"OAuth callback error: {e}")
        error_url = f"{settings.FRONTEND_URL}/auth/error?message={str(e)}"
        return RedirectResponse(url=error_url)


@router.post("/logout")
async def logout(
    response: Response,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    登出端點

    清除 Session（客戶端需自行清除 Token）
    """
    if current_user:
        logger.info(f"User logged out: {current_user.get('email')}")

    return {
        "success": True,
        "message": "已登出",
    }


@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: dict = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    取得當前登入用戶資訊

    需要在 Authorization header 提供 Bearer Token（JWT 或 API Token）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="未登入")

    user_id = current_user.get("user_id")
    auth_type = current_user.get("auth_type", "unknown")

    if auth_type == "jwt":
        # JWT 登入的用戶
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")

        return MeResponse(
            success=True,
            user=UserInfo(
                id=user.id,
                email=user.email,
                name=user.name,
                picture=user.picture,
            ),
            auth_type="oauth",
        )
    else:
        # API Token 登入
        return MeResponse(
            success=True,
            user=UserInfo(
                id=user_id or "anonymous",
                email=current_user.get("email", ""),
                name=current_user.get("name", "API User"),
                picture=None,
            ),
            auth_type="api_token",
        )


# =========================
# API Token 端點
# =========================


@router.post("/token/generate", response_model=TokenResponse)
def generate_token(
    request: GenerateTokenRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    產生新的 API Token

    此 Token 用於 Siri 捷徑等外部服務呼叫 API。
    Token 會綁定到當前登入的用戶帳號。

    **必須先登入才能產生 Token**
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="必須先登入才能產生 API Token。請先在網頁版使用 Google 帳號登入。",
        )

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="無效的用戶。請重新登入。",
        )

    logger.info(f"Generating token for user: {user_id}")

    # 產生綁定用戶的 API Token
    raw_token, api_token = create_api_token(
        db,
        description=request.description,
        user_id=user_id,
        expires_days=request.expires_in_days,
    )

    return TokenResponse(
        success=True,
        token=raw_token,
        description=api_token.description,
        created_at=api_token.created_at.isoformat(),
        expires_at=api_token.expires_at.isoformat() if api_token.expires_at else None,
        message="Token 已產生並綁定您的帳號，請妥善保管。可用於 Siri 捷徑記帳。",
    )


@router.get("/token/list", response_model=APITokenListResponse)
def list_tokens(
    current_user: dict = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    列出當前用戶的所有 API Token

    需要登入才能使用
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登入")

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="無效的用戶")

    tokens = get_user_api_tokens(db, user_id)

    return APITokenListResponse(
        success=True,
        tokens=[
            APITokenInfo(
                id=t.id,
                description=t.description,
                created_at=t.created_at.isoformat(),
                expires_at=t.expires_at.isoformat() if t.expires_at else None,
                last_used_at=t.last_used_at.isoformat() if t.last_used_at else None,
                is_active=t.is_active,
            )
            for t in tokens
        ],
    )


@router.delete("/token/{token_id}")
def delete_token(
    token_id: int,
    current_user: dict = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    撤銷 API Token

    需要登入才能使用
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登入")

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="無效的用戶")

    success = revoke_api_token(db, token_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Token 不存在或無權限")

    return {
        "success": True,
        "message": "Token 已撤銷",
    }


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
async def get_auth_status(
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    檢查認證狀態
    """
    if current_user:
        return {
            "success": True,
            "authenticated": True,
            "auth_type": current_user.get("auth_type", "unknown"),
            "user_id": current_user.get("user_id"),
        }
    else:
        return {
            "success": True,
            "authenticated": False,
            "auth_type": None,
            "user_id": None,
        }
