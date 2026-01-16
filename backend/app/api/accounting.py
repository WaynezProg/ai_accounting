"""記帳 API 端點"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.database.crud import (
    get_user_sheet,
    get_google_token,
    is_google_token_expired,
    save_google_token,
    get_user_by_id,
    create_query_history,
    get_query_history,
    get_query_history_count,
    get_user_budget,
)
from app.models.schemas import (
    AccountingRequest,
    AccountingResponse,
    QueryRequest,
    QueryResponse,
    StatsResponse,
    QueryHistoryResponse,
    QueryHistoryItem,
    DashboardSummaryResponse,
    DashboardSummary,
    MonthSummary,
    CategorySummary,
    RecentRecord,
    DailyTrend,
    BudgetStatus,
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
    智慧查詢端點（財務小助手）

    使用自然語言查詢帳務狀況、詢問理財知識，或進行日常對話

    需要在 Authorization header 提供 Bearer Token（JWT 或已綁定用戶的 API Token）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    logger.info(f"Query: {request.query}")

    # 取得用戶的 Sheets 服務
    user_sheets_service, sheet_id = await get_sheets_service_for_user(current_user, db)

    # 取得用戶時區設定
    user_id = current_user.get("user_id")
    user_timezone = "Asia/Taipei"  # 預設值
    if user_id:
        user = get_user_by_id(db, user_id)
        if user and user.timezone:
            user_timezone = user.timezone

    # 1. 取得當月統計資料
    stats = await user_sheets_service.get_monthly_stats(sheet_id)

    # 取得用戶時區的當前時間（用於日期計算）
    try:
        tz = ZoneInfo(user_timezone)
    except Exception:
        logger.warning(
            f"Invalid timezone: {user_timezone}, falling back to Asia/Taipei"
        )
        tz = ZoneInfo("Asia/Taipei")
    now_in_user_tz = datetime.now(tz)

    # 2. 取得近期消費明細（最近 7 天，基於用戶時區）
    recent_records = None
    try:
        today = now_in_user_tz.strftime("%Y-%m-%d")
        week_ago = (now_in_user_tz - timedelta(days=7)).strftime("%Y-%m-%d")
        recent_records = await user_sheets_service.get_records_by_date_range(
            sheet_id, week_ago, today
        )
    except Exception as e:
        logger.warning(f"Failed to get recent records: {e}")

    # 3. 取得近三個月統計資料（用於趨勢分析，基於用戶時區）
    multi_month_stats = None
    try:
        # 正確計算前幾個月（避免使用 timedelta(days=30) 導致月份邊界錯誤）
        months = []
        current_year = now_in_user_tz.year
        current_month = now_in_user_tz.month
        for i in range(3):
            # 計算往前 i 個月的年月
            target_month = current_month - i
            target_year = current_year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            months.append(f"{target_year:04d}-{target_month:02d}")
        multi_month_stats = await user_sheets_service.get_multi_month_stats(
            sheet_id, months
        )
    except Exception as e:
        logger.warning(f"Failed to get multi-month stats: {e}")

    # 4. 使用 LLM 回答問題（帶入完整上下文）
    response = await openai_service.answer_query(
        query=request.query,
        stats=stats,
        user_timezone=user_timezone,
        recent_records=recent_records,
        multi_month_stats=multi_month_stats,
    )

    # 5. 儲存查詢記錄到資料庫
    if user_id:
        try:
            create_query_history(db, user_id, request.query, response)
            logger.info(f"Query history saved for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to save query history: {e}")

    return QueryResponse(
        success=True,
        response=response,
    )


@router.get("/query/history", response_model=QueryHistoryResponse)
async def get_query_history_endpoint(
    limit: int = Query(20, ge=1, le=100, description="每頁筆數"),
    cursor: Optional[str] = Query(None, description="分頁游標 (ISO 8601 時間戳)"),
    search: Optional[str] = Query(None, description="搜尋關鍵字"),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    取得查詢記錄

    支援 cursor-based 分頁和搜尋功能

    需要在 Authorization header 提供 Bearer Token（JWT 或已綁定用戶的 API Token）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=403,
            detail="此 API Token 未綁定用戶帳號。請先登入網頁版產生新的 Token。",
        )

    logger.info(
        f"Getting query history for user {user_id}, search={search}, cursor={cursor}"
    )

    # 解析 cursor 時間戳
    # 注意：資料庫儲存的是 naive UTC datetime，需要將 cursor 轉換為 naive datetime
    cursor_dt = None
    if cursor:
        try:
            parsed = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
            # 如果是 timezone-aware，轉換為 UTC 後移除 tzinfo
            if parsed.tzinfo is not None:
                cursor_dt = parsed.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
            else:
                cursor_dt = parsed
        except ValueError:
            raise HTTPException(status_code=400, detail="無效的 cursor 格式")

    # 取得查詢記錄
    records, next_cursor = get_query_history(
        db, user_id, limit=limit, cursor=cursor_dt, search=search
    )

    # 取得總筆數
    total = get_query_history_count(db, user_id, search=search)

    # 轉換為回應格式
    items = [
        QueryHistoryItem(
            id=record.id,
            query=record.query,
            answer=record.answer,
            created_at=record.created_at.isoformat(),
        )
        for record in records
    ]

    return QueryHistoryResponse(
        success=True,
        items=items,
        next_cursor=next_cursor.isoformat() if next_cursor else None,
        total=total,
    )


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    取得 Dashboard 摘要資料

    一次回傳：
    - 本月消費摘要（總金額、筆數、前三大類別）
    - 最近 5 筆記帳記錄
    - 過去 7 天每日消費趨勢
    - 預算狀態

    需要在 Authorization header 提供 Bearer Token（JWT 或已綁定用戶的 API Token）
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="需要認證")

    logger.info("Getting dashboard summary")

    # 取得用戶的 Sheets 服務
    user_sheets_service, sheet_id = await get_sheets_service_for_user(current_user, db)
    user_id = current_user.get("user_id")

    # 取得用戶時區設定
    user_timezone = "Asia/Taipei"  # 預設值
    if user_id:
        user = get_user_by_id(db, user_id)
        if user and user.timezone:
            user_timezone = user.timezone

    # 1. 取得本月統計
    stats = await user_sheets_service.get_monthly_stats(sheet_id)

    # 計算前三大類別
    top_categories = []
    if stats.by_category:
        sorted_categories = sorted(
            stats.by_category.items(), key=lambda x: x[1], reverse=True
        )[:3]
        for category, amount in sorted_categories:
            percentage = (amount / stats.total * 100) if stats.total > 0 else 0
            top_categories.append(
                CategorySummary(
                    category=category, total=amount, percentage=round(percentage, 1)
                )
            )

    month_summary = MonthSummary(
        total=stats.total,
        record_count=stats.record_count,
        top_categories=top_categories,
    )

    # 2. 取得最近記帳記錄
    recent_records = []
    try:
        recent_records_raw = await user_sheets_service.get_recent_records(
            sheet_id, limit=5
        )
        recent_records = [
            RecentRecord(
                時間=r.get("時間", ""),
                名稱=r.get("名稱", ""),
                類別=r.get("類別", ""),
                花費=float(r.get("花費", 0)),
            )
            for r in recent_records_raw
        ]
    except Exception as e:
        logger.warning(f"Failed to get recent records for dashboard: {e}")

    # 3. 取得每日消費趨勢（使用用戶時區）
    daily_trend = []
    try:
        daily_trend_raw = await user_sheets_service.get_daily_trend(
            sheet_id, days=7, user_timezone=user_timezone
        )
        daily_trend = [
            DailyTrend(date=d["date"], total=d["total"]) for d in daily_trend_raw
        ]
    except Exception as e:
        logger.warning(f"Failed to get daily trend for dashboard: {e}")

    # 4. 取得預算狀態
    monthly_limit = get_user_budget(db, user_id) if user_id else None
    # Use "is not None" to distinguish between "not set" (None) and "set to 0"
    has_budget = monthly_limit is not None
    budget = BudgetStatus(
        monthly_limit=monthly_limit,
        spent=stats.total,
        remaining=(monthly_limit - stats.total) if has_budget else None,
        percentage=(
            # Handle division by zero: if limit is 0 and spent > 0, it's infinitely over budget (cap at 100%)
            round(stats.total / monthly_limit * 100, 1)
            if has_budget and monthly_limit > 0
            else (
                100.0 if has_budget and stats.total > 0 else 0.0 if has_budget else None
            )
        ),
    )

    # 組合回傳
    dashboard = DashboardSummary(
        month_summary=month_summary,
        recent_records=recent_records,
        daily_trend=daily_trend,
        budget=budget,
    )

    logger.info(f"Dashboard summary: total={stats.total}, records={stats.record_count}")

    return DashboardSummaryResponse(success=True, data=dashboard)


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
