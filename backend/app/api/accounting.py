"""記帳 API 端點"""

import logging
from typing import Optional

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.database.crud import (
    get_user_sheet,
    get_google_token,
    is_google_token_expired,
    save_google_token,
)
from app.models.schemas import (
    AccountingRequest,
    AccountingResponse,
    QueryRequest,
    QueryResponse,
    StatsResponse,
)
from app.services.openai_service import openai_service
from app.services.user_sheets_service import create_user_sheets_service
from app.services.oauth_service import oauth_service
from app.utils.categories import DEFAULT_CATEGORIES
from app.utils.auth import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_sheets_service_for_user(
    current_user: Optional[dict],
    db: Session,
):
    """
    取得用戶的 Sheets 服務和 Sheet ID

    所有記帳都必須使用 OAuth 認證，寫入用戶專屬的 Sheet。

    Returns:
        (sheets_service, sheet_id) 或拋出 HTTPException
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    user_id = current_user.get("user_id")

    # 必須有綁定用戶
    if not user_id:
        raise HTTPException(
            status_code=403,
            detail="此 API Token 未綁定用戶帳號。請先登入網頁版產生新的 Token。",
        )

    # 取得用戶的 Sheet 資訊
    user_sheet = get_user_sheet(db, user_id)
    if not user_sheet:
        raise HTTPException(
            status_code=400,
            detail="尚未設定 Google Sheet。請先登入網頁版並建立或連結 Sheet。",
        )

    # 取得用戶的 Google Token
    google_token = get_google_token(db, user_id)
    if not google_token:
        raise HTTPException(
            status_code=400,
            detail="Google 授權已失效。請重新登入網頁版授權。",
        )

    # 檢查並刷新 Token
    if is_google_token_expired(google_token):
        if not google_token.refresh_token:
            raise HTTPException(
                status_code=400,
                detail="Google 授權已過期且無法自動刷新。請重新登入網頁版授權。",
            )

        try:
            new_access_token, new_expires_at = await oauth_service.refresh_access_token(
                google_token.refresh_token
            )
            google_token = save_google_token(
                db,
                user_id=user_id,
                access_token=new_access_token,
                refresh_token=google_token.refresh_token,
                expires_at=new_expires_at,
            )
            logger.info(f"Token refreshed for user {user_id}")
        except Exception as e:
            logger.error(f"Token refresh failed for user {user_id}: {e}")
            raise HTTPException(
                status_code=400,
                detail="Google 授權刷新失敗。請重新登入網頁版授權。",
            )

    # 建立用戶專屬的 Sheets 服務
    sheets_service = create_user_sheets_service(
        access_token=google_token.access_token,
        refresh_token=google_token.refresh_token,
        expires_at=google_token.expires_at,
    )

    return sheets_service, user_sheet.sheet_id


@router.post("/record", response_model=AccountingResponse)
async def record_accounting(
    request: AccountingRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    記帳端點

    接收語音轉文字內容，使用 LLM 解析後寫入用戶專屬的 Google Sheet。

    需要在 Authorization header 提供 Bearer Token（JWT 或已綁定用戶的 API Token）

    使用條件：
    - 必須登入或使用已綁定用戶的 API Token
    - 必須已建立或連結 Google Sheet
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    logger.info(f"Recording: {request.text}")

    # 1. 使用 LLM 解析記帳文字
    record = await openai_service.parse_accounting_text(request.text)

    # 2. 取得用戶的 Sheets 服務（會驗證所有必要條件）
    user_sheets_service, sheet_id = await get_sheets_service_for_user(current_user, db)

    # 3. 寫入用戶專屬的 Google Sheet
    await user_sheets_service.write_record(sheet_id, record)
    logger.info(f"Written to user sheet: {sheet_id}")

    # 4. 取得統計資料並生成理財回饋
    try:
        stats = await user_sheets_service.get_monthly_stats(sheet_id)
        feedback = await openai_service.generate_feedback(record, stats)
    except Exception as e:
        logger.warning(f"Failed to generate feedback: {e}")
        feedback = None

    # 5. 回傳結果
    return AccountingResponse(
        success=True,
        record=record,
        message=f"已記錄：{record.名稱} {record.花費}{record.幣別}",
        feedback=feedback,
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    month: Optional[str] = Query(None, description="月份，格式：YYYY-MM"),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    取得月度統計資料

    如果未指定月份，則回傳當月統計

    需要在 Authorization header 提供 Bearer Token（JWT 或已綁定用戶的 API Token）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    logger.info(f"Getting stats for month: {month or 'current'}")

    # 取得用戶的 Sheets 服務
    user_sheets_service, sheet_id = await get_sheets_service_for_user(current_user, db)
    stats = await user_sheets_service.get_monthly_stats(sheet_id, month)

    return StatsResponse(
        success=True,
        data=stats,
    )


@router.post("/query", response_model=QueryResponse)
async def query_accounting(
    request: QueryRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    帳務查詢端點

    使用自然語言查詢帳務狀況

    需要在 Authorization header 提供 Bearer Token（JWT 或已綁定用戶的 API Token）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    logger.info(f"Query: {request.query}")

    # 取得用戶的 Sheets 服務
    user_sheets_service, sheet_id = await get_sheets_service_for_user(current_user, db)

    # 1. 取得統計資料
    stats = await user_sheets_service.get_monthly_stats(sheet_id)

    # 2. 使用 LLM 回答問題
    response = await openai_service.answer_query(request.query, stats)

    return QueryResponse(
        success=True,
        response=response,
    )


@router.get("/categories")
async def get_categories():
    """
    取得預設類別清單

    此端點不需要認證
    """
    return {
        "success": True,
        "categories": DEFAULT_CATEGORIES,
    }
