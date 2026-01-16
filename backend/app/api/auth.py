"""認證 API 端點"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
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
    save_refresh_token,
    get_refresh_token_by_hash,
    revoke_refresh_token,
    update_refresh_token_usage,
    update_user_timezone,
    create_oauth_login_code,
    get_oauth_login_code_by_hash,
    mark_oauth_login_code_used,
    get_user_budget,
    update_user_budget,
)
from app.services.oauth_service import oauth_service
from app.services.jwt_service import jwt_service
from app.utils.auth import verify_token, get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter()

# OAuth state 已改由前端管理（存在 sessionStorage）
# 不再需要後端暫存，避免多實例和 cold start 問題


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


class RefreshTokenRequest(BaseModel):
    """Refresh Token 請求"""

    refresh_token: str = Field(..., description="Refresh Token")


class AuthSessionResponse(BaseModel):
    """登入/刷新回應"""

    success: bool = True
    access_token: str
    refresh_token: str
    access_token_expires_at: str
    token_type: str
    auth_type: str


class ExchangeCodeRequest(BaseModel):
    """交換 one-time code 請求"""

    code: str = Field(..., description="OAuth one-time code")


class ExchangeGoogleCodeRequest(BaseModel):
    """交換 Google 授權碼請求"""

    code: str = Field(..., description="Google 授權碼 (authorization code)")
    # state 驗證已移至前端 sessionStorage，後端不再驗證


class ExchangeGoogleCodeResponse(BaseModel):
    """交換 Google 授權碼回應"""

    success: bool = True
    code: str = Field(..., description="One-time code（用於交換 JWT）")
    new_user: bool = Field(..., description="是否為新用戶")


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
async def google_login(
    state: str = Query(..., description="前端生成的 CSRF state 參數"),
):
    """
    開始 Google OAuth 登入流程

    重導向至 Google 授權頁面。
    state 參數由前端生成並存在 sessionStorage，用於 CSRF 防護。
    """
    auth_url = oauth_service.get_authorization_url(state)
    logger.info(f"Redirecting to Google OAuth, state: {state[:8]}...")
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Google 授權碼"),
    state: str = Query(None, description="CSRF state 參數（已移至前端驗證）"),
    db: Session = Depends(get_db),
):
    """
    Google OAuth 回調端點（舊版，保留相容性）

    處理 Google 授權後的回調，建立用戶並發放 JWT。
    新流程建議使用 POST /api/auth/google/exchange-code。
    注意：state 驗證已移至前端 sessionStorage。
    """
    # state 驗證已移至前端，後端不再驗證
    if state:
        logger.info(
            f"Google callback received state: {state[:8]}... (validation moved to frontend)"
        )

    try:
        # 2. 交換授權碼為 Token
        (
            access_token,
            refresh_token,
            expires_at,
        ) = await oauth_service.exchange_code_for_tokens(code)

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

        # 6. 建立 one-time code（交換用）
        raw_code = secrets.token_urlsafe(32)
        code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.OAUTH_CODE_EXPIRE_MINUTES
        )
        create_oauth_login_code(
            db,
            user_id=user.id,
            code_hash=code_hash,
            expires_at=expires_at,
        )

        # 7. 重導向至前端，帶上 one-time code
        params = {
            "code": raw_code,
            "new_user": "1" if is_new else "0",
        }
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback#{urlencode(params)}"

        logger.info(f"OAuth success for user: {user.email}, new: {is_new}")
        return RedirectResponse(url=redirect_url)

    except ValueError as e:
        logger.error(f"OAuth callback error: {e}")
        error_url = f"{settings.FRONTEND_URL}/auth/error?message={str(e)}"
        return RedirectResponse(url=error_url)


@router.post("/google/exchange-code", response_model=ExchangeGoogleCodeResponse)
async def exchange_google_code(
    request: ExchangeGoogleCodeRequest,
    db: Session = Depends(get_db),
):
    """
    交換 Google 授權碼

    前端從 Google OAuth callback 取得授權碼後，
    透過此端點交換為 one-time code，再用於取得 JWT。

    流程：
    1. 前端接收 Google callback（含 code 和 state）
    2. 前端驗證 state 與 sessionStorage 一致（CSRF 防護）
    3. 前端呼叫此端點，傳送 code
    4. 後端向 Google 交換 token，建立用戶資料
    5. 後端產生 one-time code
    6. 前端用 one-time code 呼叫 /api/auth/exchange 取得 JWT
    """
    # state 驗證已移至前端 sessionStorage，後端不再驗證

    try:
        # 2. 交換授權碼為 Token
        (
            access_token,
            refresh_token,
            token_expires_at,
        ) = await oauth_service.exchange_code_for_tokens(request.code)

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
            expires_at=token_expires_at,
            scope=" ".join(settings.GOOGLE_OAUTH_SCOPES),
        )

        # 6. 建立 one-time code（交換用）
        raw_code = secrets.token_urlsafe(32)
        code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
        code_expires_at = datetime.utcnow() + timedelta(
            minutes=settings.OAUTH_CODE_EXPIRE_MINUTES
        )
        create_oauth_login_code(
            db,
            user_id=user.id,
            code_hash=code_hash,
            expires_at=code_expires_at,
        )

        logger.info(
            f"OAuth exchange-code success for user: {user.email}, new: {is_new}"
        )

        return ExchangeGoogleCodeResponse(
            success=True,
            code=raw_code,
            new_user=is_new,
        )

    except ValueError as e:
        logger.error(f"OAuth exchange-code error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(
    response: Response,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    登出端點

    清除 Session（客戶端需自行清除 Token）
    """
    if current_user:
        logger.info(f"User logged out: {current_user.get('email')}")
        user_id = current_user.get("user_id")
        if user_id:
            revoke_refresh_token(db, user_id)

    return {
        "success": True,
        "message": "已登出",
    }


@router.post("/refresh", response_model=AuthSessionResponse)
def refresh_session(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    使用 Refresh Token 取得新的 Access Token
    """
    token_hash = jwt_service.hash_refresh_token(request.refresh_token)
    token_record = get_refresh_token_by_hash(db, token_hash)

    if not token_record or token_record.revoked_at:
        raise HTTPException(status_code=401, detail="Refresh token 無效")

    now = datetime.utcnow()

    if token_record.expires_at and now >= token_record.expires_at:
        token_record.revoked_at = now
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token 已過期")

    last_used_at = token_record.last_used_at or token_record.issued_at
    if now - last_used_at > timedelta(hours=settings.JWT_REFRESH_INACTIVITY_HOURS):
        token_record.revoked_at = now
        db.commit()
        raise HTTPException(status_code=401, detail="Session 已過期，請重新登入")

    # 更新 last_used_at 以重置 inactivity 計時器
    update_refresh_token_usage(db, token_record)

    user = get_user_by_id(db, token_record.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")

    access_token, access_expires_at = jwt_service.create_access_token_with_expiry(
        user_id=user.id,
        email=user.email,
    )

    new_refresh_token = jwt_service.create_refresh_token()
    new_refresh_hash = jwt_service.hash_refresh_token(new_refresh_token)
    refresh_expires_at = None
    if settings.JWT_REFRESH_EXPIRE_HOURS > 0:
        refresh_expires_at = now + timedelta(hours=settings.JWT_REFRESH_EXPIRE_HOURS)

    save_refresh_token(
        db,
        user_id=user.id,
        token_hash=new_refresh_hash,
        expires_at=refresh_expires_at,
    )

    return AuthSessionResponse(
        success=True,
        access_token=access_token,
        refresh_token=new_refresh_token,
        access_token_expires_at=access_expires_at.replace(
            tzinfo=timezone.utc
        ).isoformat(),
        token_type="Bearer",
        auth_type="oauth",
    )


@router.post("/exchange", response_model=AuthSessionResponse)
def exchange_oauth_code(
    request: ExchangeCodeRequest,
    db: Session = Depends(get_db),
):
    """
    使用 OAuth one-time code 交換 Access Token
    """
    code_hash = hashlib.sha256(request.code.encode()).hexdigest()
    code_record = get_oauth_login_code_by_hash(db, code_hash)

    if not code_record or code_record.used_at:
        raise HTTPException(status_code=401, detail="交換碼無效")

    now = datetime.utcnow()
    if now >= code_record.expires_at:
        raise HTTPException(status_code=401, detail="交換碼已過期")

    mark_oauth_login_code_used(db, code_record)

    user = get_user_by_id(db, code_record.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")

    access_token, access_expires_at = jwt_service.create_access_token_with_expiry(
        user_id=user.id,
        email=user.email,
    )

    new_refresh_token = jwt_service.create_refresh_token()
    new_refresh_hash = jwt_service.hash_refresh_token(new_refresh_token)
    refresh_expires_at = None
    if settings.JWT_REFRESH_EXPIRE_HOURS > 0:
        refresh_expires_at = now + timedelta(hours=settings.JWT_REFRESH_EXPIRE_HOURS)

    save_refresh_token(
        db,
        user_id=user.id,
        token_hash=new_refresh_hash,
        expires_at=refresh_expires_at,
    )

    return AuthSessionResponse(
        success=True,
        access_token=access_token,
        refresh_token=new_refresh_token,
        access_token_expires_at=access_expires_at.replace(
            tzinfo=timezone.utc
        ).isoformat(),
        token_type="Bearer",
        auth_type="oauth",
    )


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


# =========================
# 用戶設定端點
# =========================


class UpdateTimezoneRequest(BaseModel):
    """更新時區請求"""

    timezone: str = Field(
        ...,
        description="IANA 時區名稱，如 Asia/Taipei、America/New_York",
        examples=["Asia/Taipei", "America/New_York", "Europe/London"],
    )


class TimezoneResponse(BaseModel):
    """時區回應"""

    success: bool = True
    timezone: str
    message: str


# 常用時區列表
COMMON_TIMEZONES = [
    "Asia/Taipei",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Hong_Kong",
    "Asia/Singapore",
    "America/New_York",
    "America/Los_Angeles",
    "America/Chicago",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Australia/Sydney",
    "Pacific/Auckland",
]


@router.get("/settings/timezone", response_model=TimezoneResponse)
def get_timezone(
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    取得用戶的時區設定
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登入")

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="無效的用戶")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")

    return TimezoneResponse(
        success=True,
        timezone=user.timezone or "Asia/Taipei",
        message="取得成功",
    )


@router.put("/settings/timezone", response_model=TimezoneResponse)
def update_timezone(
    request: UpdateTimezoneRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    更新用戶的時區設定

    時區必須是有效的 IANA 時區名稱（如 Asia/Taipei、America/New_York）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登入")

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="無效的用戶")

    # 驗證時區是否有效
    from zoneinfo import ZoneInfo

    try:
        ZoneInfo(request.timezone)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"無效的時區：{request.timezone}。請使用 IANA 時區名稱，如 Asia/Taipei",
        )

    user = update_user_timezone(db, user_id, request.timezone)
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")

    logger.info(f"Updated timezone for user {user_id}: {request.timezone}")

    return TimezoneResponse(
        success=True,
        timezone=user.timezone,
        message="時區更新成功",
    )


@router.get("/settings/timezones")
def list_timezones():
    """
    取得常用時區列表
    """
    return {
        "success": True,
        "timezones": COMMON_TIMEZONES,
    }


# =========================
# 預算設定端點
# =========================


class BudgetRequest(BaseModel):
    """預算設定請求"""

    monthly_budget: Optional[int] = Field(
        default=None,
        description="月預算金額（null 表示取消預算）",
        ge=0,
    )


class BudgetResponse(BaseModel):
    """預算回應"""

    success: bool = True
    monthly_budget: Optional[int] = None
    message: str = ""


@router.get("/settings/budget", response_model=BudgetResponse)
def get_budget(
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    取得用戶的月預算設定
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登入")

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="無效的用戶")

    budget = get_user_budget(db, user_id)

    return BudgetResponse(
        success=True,
        monthly_budget=budget,
        message="取得成功",
    )


@router.put("/settings/budget", response_model=BudgetResponse)
def set_budget(
    request: BudgetRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    設定用戶的月預算

    傳入 monthly_budget = null 可取消預算設定
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登入")

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="無效的用戶")

    user = update_user_budget(db, user_id, request.monthly_budget)
    if not user:
        raise HTTPException(status_code=404, detail="用戶不存在")

    if request.monthly_budget is None:
        message = "已取消月預算設定"
    else:
        message = f"月預算已設定為 {request.monthly_budget:,} 元"

    logger.info(f"Updated budget for user {user_id}: {request.monthly_budget}")

    return BudgetResponse(
        success=True,
        monthly_budget=user.monthly_budget,
        message=message,
    )
