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
from app.services.google_sheets import google_sheets_service
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
    根據用戶類型取得對應的 Sheets 服務和 Sheet ID

    - OAuth 用戶：使用用戶專屬的 Sheet
    - API Token 用戶（有綁定用戶）：使用綁定用戶的 Sheet
    - 匿名 API Token：使用共用 Service Account Sheet

    Returns:
        (sheets_service, sheet_id) 或 (None, None) 表示使用共用 Sheet
    """
    if not current_user:
        return None, None

    user_id = current_user.get("user_id")
    auth_type = current_user.get("auth_type")

    # 沒有綁定用戶的 API Token 使用共用 Sheet
    if not user_id:
        return None, None

    # 取得用戶的 Sheet 資訊
    user_sheet = get_user_sheet(db, user_id)
    if not user_sheet:
        # 用戶尚未建立 Sheet，使用共用 Sheet
        return None, None

    # 取得用戶的 Google Token
    google_token = get_google_token(db, user_id)
    if not google_token:
        # 沒有 Google Token，使用共用 Sheet
        return None, None

    # 檢查並刷新 Token
    if is_google_token_expired(google_token):
        if not google_token.refresh_token:
            logger.warning(f"Token expired for user {user_id}, no refresh token")
            return None, None

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
        except Exception as e:
            logger.error(f"Token refresh failed for user {user_id}: {e}")
            return None, None

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

    接收語音轉文字內容，使用 LLM 解析後寫入 Google Sheets

    需要在 Authorization header 提供 Bearer Token（JWT 或 API Token）

    - OAuth 登入用戶：寫入用戶專屬 Sheet
    - API Token（已綁定用戶）：寫入綁定用戶的 Sheet
    - API Token（未綁定用戶）：寫入共用 Sheet
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    logger.info(f"Recording: {request.text}")

    # 1. 使用 LLM 解析記帳文字
    record = await openai_service.parse_accounting_text(request.text)

    # 2. 取得對應的 Sheets 服務
    user_sheets_service, sheet_id = await get_sheets_service_for_user(current_user, db)

    # 3. 寫入 Google Sheets
    if user_sheets_service and sheet_id:
        # 使用用戶專屬 Sheet
        await user_sheets_service.write_record(sheet_id, record)
        logger.info(f"Written to user sheet: {sheet_id}")
    else:
        # 使用共用 Sheet（Service Account 模式）
        await google_sheets_service.write_record(record)
        logger.info("Written to shared sheet")

    # 4. 取得統計資料並生成理財回饋
    try:
        if user_sheets_service and sheet_id:
            stats = await user_sheets_service.get_monthly_stats(sheet_id)
        else:
            stats = await google_sheets_service.get_monthly_stats()
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

    需要在 Authorization header 提供 Bearer Token（JWT 或 API Token）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    logger.info(f"Getting stats for month: {month or 'current'}")

    # 取得對應的 Sheets 服務
    user_sheets_service, sheet_id = await get_sheets_service_for_user(current_user, db)

    if user_sheets_service and sheet_id:
        stats = await user_sheets_service.get_monthly_stats(sheet_id, month)
    else:
        stats = await google_sheets_service.get_monthly_stats(month)

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

    需要在 Authorization header 提供 Bearer Token（JWT 或 API Token）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    logger.info(f"Query: {request.query}")

    # 取得對應的 Sheets 服務
    user_sheets_service, sheet_id = await get_sheets_service_for_user(current_user, db)

    # 1. 取得統計資料
    if user_sheets_service and sheet_id:
        stats = await user_sheets_service.get_monthly_stats(sheet_id)
    else:
        stats = await google_sheets_service.get_monthly_stats()

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
