"""記帳 API 端點"""

import logging
from typing import Optional

from fastapi import APIRouter, Query, Depends

from app.models.schemas import (
    AccountingRequest,
    AccountingResponse,
    QueryRequest,
    QueryResponse,
    StatsResponse,
)
from app.services.openai_service import openai_service
from app.services.google_sheets import google_sheets_service
from app.utils.categories import DEFAULT_CATEGORIES
from app.utils.auth import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/record", response_model=AccountingResponse)
async def record_accounting(
    request: AccountingRequest,
    token_valid: bool = Depends(verify_token),
):
    """
    記帳端點

    接收語音轉文字內容，使用 LLM 解析後寫入 Google Sheets

    需要在 Authorization header 提供 Bearer Token
    """
    logger.info(f"Recording: {request.text}")

    # 1. 使用 LLM 解析記帳文字
    record = await openai_service.parse_accounting_text(request.text)

    # 2. 寫入 Google Sheets
    await google_sheets_service.write_record(record)

    # 3. 取得統計資料並生成理財回饋
    try:
        stats = await google_sheets_service.get_monthly_stats()
        feedback = await openai_service.generate_feedback(record, stats)
    except Exception as e:
        logger.warning(f"Failed to generate feedback: {e}")
        feedback = None

    # 4. 回傳結果
    return AccountingResponse(
        success=True,
        record=record,
        message=f"已記錄：{record.名稱} {record.花費}{record.幣別}",
        feedback=feedback,
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    month: Optional[str] = Query(None, description="月份，格式：YYYY-MM"),
    token_valid: bool = Depends(verify_token),
):
    """
    取得月度統計資料

    如果未指定月份，則回傳當月統計

    需要在 Authorization header 提供 Bearer Token
    """
    logger.info(f"Getting stats for month: {month or 'current'}")

    stats = await google_sheets_service.get_monthly_stats(month)

    return StatsResponse(
        success=True,
        data=stats,
    )


@router.post("/query", response_model=QueryResponse)
async def query_accounting(
    request: QueryRequest,
    token_valid: bool = Depends(verify_token),
):
    """
    帳務查詢端點

    使用自然語言查詢帳務狀況

    需要在 Authorization header 提供 Bearer Token
    """
    logger.info(f"Query: {request.query}")

    # 1. 取得統計資料
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
