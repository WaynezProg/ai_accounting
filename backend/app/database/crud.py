"""資料庫 CRUD 操作"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    User,
    GoogleToken,
    APIToken,
    UserSheet,
    RefreshToken,
    OAuthLoginCode,
)

logger = logging.getLogger(__name__)


# =========================
# User CRUD
# =========================


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """根據 ID 取得用戶"""
    result = db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根據 Email 取得用戶"""
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def create_user(
    db: Session,
    user_id: str,
    email: str,
    name: str,
    picture: Optional[str] = None,
) -> User:
    """建立新用戶"""
    user = User(
        id=user_id,
        email=email,
        name=name,
        picture=picture,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Created user: {email}")
    return user


def update_user(
    db: Session,
    user: User,
    name: Optional[str] = None,
    picture: Optional[str] = None,
    timezone: Optional[str] = None,
) -> User:
    """更新用戶資料"""
    if name is not None:
        user.name = name
    if picture is not None:
        user.picture = picture
    if timezone is not None:
        user.timezone = timezone
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def update_user_timezone(db: Session, user_id: str, timezone: str) -> Optional[User]:
    """更新用戶時區設定"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.timezone = timezone
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    logger.info(f"Updated timezone for user {user_id}: {timezone}")
    return user


def get_or_create_user(
    db: Session,
    user_id: str,
    email: str,
    name: str,
    picture: Optional[str] = None,
) -> tuple[User, bool]:
    """取得或建立用戶，回傳 (user, is_new)"""
    user = get_user_by_id(db, user_id)
    if user:
        # 更新用戶資料
        user = update_user(db, user, name=name, picture=picture)
        return user, False
    else:
        user = create_user(db, user_id, email, name, picture)
        return user, True


# =========================
# GoogleToken CRUD
# =========================


def get_google_token(db: Session, user_id: str) -> Optional[GoogleToken]:
    """取得用戶的 Google Token"""
    result = db.execute(
        select(GoogleToken).where(GoogleToken.user_id == user_id)
    )
    return result.scalar_one_or_none()


def save_google_token(
    db: Session,
    user_id: str,
    access_token: str,
    refresh_token: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    scope: Optional[str] = None,
) -> GoogleToken:
    """儲存或更新 Google Token"""
    token = get_google_token(db, user_id)

    if token:
        # 更新現有 Token
        token.access_token = access_token
        if refresh_token:
            token.refresh_token = refresh_token
        token.expires_at = expires_at
        token.scope = scope
        token.updated_at = datetime.utcnow()
    else:
        # 建立新 Token
        token = GoogleToken(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scope=scope,
        )
        db.add(token)

    db.commit()
    db.refresh(token)
    return token


def is_google_token_expired(token: GoogleToken) -> bool:
    """檢查 Google Token 是否過期"""
    if not token.expires_at:
        return False
    # 提前 5 分鐘視為過期
    return datetime.utcnow() >= token.expires_at - timedelta(minutes=5)


# =========================
# APIToken CRUD
# =========================


def hash_token(token: str) -> str:
    """將 Token 進行 SHA256 雜湊"""
    return hashlib.sha256(token.encode()).hexdigest()


# =========================
# RefreshToken CRUD
# =========================


def get_refresh_token_by_hash(db: Session, token_hash: str) -> Optional[RefreshToken]:
    """根據 hash 取得 Refresh Token"""
    result = db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    return result.scalar_one_or_none()


def get_refresh_token_by_user(db: Session, user_id: str) -> Optional[RefreshToken]:
    """取得用戶的 Refresh Token"""
    result = db.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id)
    )
    return result.scalar_one_or_none()


def save_refresh_token(
    db: Session,
    user_id: str,
    token_hash: str,
    expires_at: Optional[datetime] = None,
) -> RefreshToken:
    """儲存或更新 Refresh Token（單一裝置）"""
    now = datetime.utcnow()
    token = get_refresh_token_by_user(db, user_id)

    if token:
        token.token_hash = token_hash
        token.issued_at = now
        token.last_used_at = now
        token.expires_at = expires_at
        token.revoked_at = None
    else:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            issued_at=now,
            last_used_at=now,
            expires_at=expires_at,
            revoked_at=None,
        )
        db.add(token)

    db.commit()
    db.refresh(token)
    return token


def update_refresh_token_usage(
    db: Session,
    token: RefreshToken,
) -> RefreshToken:
    """更新 Refresh Token 使用時間"""
    token.last_used_at = datetime.utcnow()
    db.commit()
    db.refresh(token)
    return token


def revoke_refresh_token(db: Session, user_id: str) -> bool:
    """撤銷 Refresh Token"""
    token = get_refresh_token_by_user(db, user_id)
    if not token:
        return False
    token.revoked_at = datetime.utcnow()
    db.commit()
    return True


# =========================
# OAuth one-time code CRUD
# =========================


def create_oauth_login_code(
    db: Session,
    user_id: str,
    code_hash: str,
    expires_at: datetime,
) -> OAuthLoginCode:
    """建立 OAuth one-time code"""
    code = OAuthLoginCode(
        user_id=user_id,
        code_hash=code_hash,
        issued_at=datetime.utcnow(),
        expires_at=expires_at,
        used_at=None,
    )
    db.add(code)
    db.commit()
    db.refresh(code)
    return code


def get_oauth_login_code_by_hash(
    db: Session, code_hash: str
) -> Optional[OAuthLoginCode]:
    """依 hash 取得 OAuth one-time code"""
    result = db.execute(
        select(OAuthLoginCode).where(OAuthLoginCode.code_hash == code_hash)
    )
    return result.scalar_one_or_none()


def mark_oauth_login_code_used(
    db: Session, code: OAuthLoginCode
) -> OAuthLoginCode:
    """標記 OAuth one-time code 已使用"""
    code.used_at = datetime.utcnow()
    db.commit()
    db.refresh(code)
    return code


def generate_api_token() -> str:
    """產生隨機 API Token"""
    return secrets.token_urlsafe(32)


def create_api_token(
    db: Session,
    description: str,
    user_id: Optional[str] = None,
    expires_days: Optional[int] = None,
) -> tuple[str, APIToken]:
    """建立 API Token，回傳 (原始 token, token 記錄)"""
    raw_token = generate_api_token()
    token_hash = hash_token(raw_token)

    expires_at = None
    if expires_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

    api_token = APIToken(
        token_hash=token_hash,
        user_id=user_id,
        description=description,
        expires_at=expires_at,
    )
    db.add(api_token)
    db.commit()
    db.refresh(api_token)

    logger.info(f"Created API token: {description} for user: {user_id}")
    return raw_token, api_token


def get_api_token_by_hash(db: Session, token_hash: str) -> Optional[APIToken]:
    """根據 hash 取得 API Token"""
    result = db.execute(
        select(APIToken).where(
            APIToken.token_hash == token_hash,
            APIToken.is_active == True,
        )
    )
    return result.scalar_one_or_none()


def verify_api_token(db: Session, raw_token: str) -> Optional[APIToken]:
    """驗證 API Token，回傳 Token 記錄或 None"""
    token_hash = hash_token(raw_token)
    token = get_api_token_by_hash(db, token_hash)

    if not token:
        return None

    # 檢查是否過期
    if token.expires_at and datetime.utcnow() >= token.expires_at:
        return None

    # 更新最後使用時間
    token.last_used_at = datetime.utcnow()
    db.commit()

    return token


def get_user_api_tokens(db: Session, user_id: str) -> list[APIToken]:
    """取得用戶的所有 API Token"""
    result = db.execute(
        select(APIToken).where(
            APIToken.user_id == user_id,
            APIToken.is_active == True,
        )
    )
    return list(result.scalars().all())


def revoke_api_token(db: Session, token_id: int, user_id: str) -> bool:
    """撤銷 API Token"""
    result = db.execute(
        select(APIToken).where(
            APIToken.id == token_id,
            APIToken.user_id == user_id,
        )
    )
    token = result.scalar_one_or_none()

    if not token:
        return False

    token.is_active = False
    db.commit()
    logger.info(f"Revoked API token: {token_id}")
    return True


# =========================
# UserSheet CRUD
# =========================


def get_user_sheet(db: Session, user_id: str) -> Optional[UserSheet]:
    """取得用戶的 Sheet 資訊"""
    result = db.execute(
        select(UserSheet).where(UserSheet.user_id == user_id)
    )
    return result.scalar_one_or_none()


def save_user_sheet(
    db: Session,
    user_id: str,
    sheet_id: str,
    sheet_url: str,
    sheet_name: str = "記帳紀錄",
) -> UserSheet:
    """儲存用戶的 Sheet 資訊"""
    user_sheet = get_user_sheet(db, user_id)

    if user_sheet:
        user_sheet.sheet_id = sheet_id
        user_sheet.sheet_url = sheet_url
        user_sheet.sheet_name = sheet_name
    else:
        user_sheet = UserSheet(
            user_id=user_id,
            sheet_id=sheet_id,
            sheet_url=sheet_url,
            sheet_name=sheet_name,
        )
        db.add(user_sheet)

    db.commit()
    db.refresh(user_sheet)
    return user_sheet
