"""Pydantic 資料模型"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# =========================
# 記帳相關
# =========================


class AccountingRequest(BaseModel):
    """記帳請求"""

    text: str = Field(..., description="語音轉文字內容", example="中午吃排骨便當120元")


class AccountingRecord(BaseModel):
    """記帳記錄"""

    時間: str = Field(..., description="記帳時間", example="2024-01-15 12:30")
    名稱: str = Field(..., description="花費內容名稱", example="排骨便當")
    類別: str = Field(..., description="消費類別", example="飲食")
    花費: float = Field(..., description="金額", example=120.0)
    幣別: str = Field(default="TWD", description="貨幣類型", example="TWD")
    支付方式: Optional[str] = Field(
        default=None, description="支付方式", example="現金"
    )


class AccountingResponse(BaseModel):
    """記帳回應"""

    success: bool = True
    record: AccountingRecord
    message: str
    feedback: Optional[str] = Field(default=None, description="理財回饋建議")


# =========================
# 查詢相關
# =========================


class QueryRequest(BaseModel):
    """帳務查詢請求"""

    query: str = Field(..., description="查詢問題", example="這個月花了多少錢？")


class QueryResponse(BaseModel):
    """帳務查詢回應"""

    success: bool = True
    response: str


# =========================
# 查詢記錄相關
# =========================


class QueryHistoryItem(BaseModel):
    """查詢記錄項目"""

    id: int
    query: str = Field(..., description="使用者的問題")
    answer: str = Field(..., description="AI 的回答")
    created_at: str = Field(..., description="查詢時間 (ISO 8601)")


class QueryHistoryResponse(BaseModel):
    """查詢記錄回應"""

    success: bool = True
    items: list[QueryHistoryItem] = Field(
        default_factory=list, description="查詢記錄列表"
    )
    next_cursor: Optional[str] = Field(
        default=None, description="下一頁游標 (ISO 8601 時間戳)"
    )
    total: int = Field(..., description="符合條件的總筆數")


# =========================
# 統計相關
# =========================


class CategoryStats(BaseModel):
    """類別統計"""

    category: str
    amount: float
    count: int
    percentage: float


class MonthlyStats(BaseModel):
    """月度統計"""

    month: str = Field(..., description="月份", example="2024-01")
    total: float = Field(..., description="總支出")
    record_count: int = Field(..., description="記錄筆數")
    by_category: Dict[str, float] = Field(..., description="各類別金額")
    by_category_count: Dict[str, int] = Field(..., description="各類別筆數")


class StatsResponse(BaseModel):
    """統計回應"""

    success: bool = True
    data: MonthlyStats


# =========================
# Dashboard Summary 相關
# =========================


class CategorySummary(BaseModel):
    """類別摘要"""

    category: str
    total: float
    percentage: float


class MonthSummary(BaseModel):
    """本月消費摘要"""

    total: float = Field(default=0, description="本月總支出")
    record_count: int = Field(default=0, description="記錄筆數")
    top_categories: List[CategorySummary] = Field(
        default_factory=list, description="前三大類別"
    )


class RecentRecord(BaseModel):
    """最近記帳記錄"""

    時間: str
    名稱: str
    類別: str
    花費: float


class DailyTrend(BaseModel):
    """每日消費趨勢"""

    date: str
    total: float


class BudgetStatus(BaseModel):
    """預算狀態"""

    monthly_limit: Optional[int] = Field(default=None, description="月預算上限")
    spent: float = Field(default=0, description="已花費金額")
    remaining: Optional[float] = Field(default=None, description="剩餘金額")
    percentage: Optional[float] = Field(default=None, description="使用百分比")


class DashboardSummary(BaseModel):
    """Dashboard 摘要資料"""

    month_summary: MonthSummary
    recent_records: List[RecentRecord] = Field(default_factory=list)
    daily_trend: List[DailyTrend] = Field(default_factory=list)
    budget: BudgetStatus


class DashboardSummaryResponse(BaseModel):
    """Dashboard 摘要回應"""

    success: bool = True
    data: DashboardSummary


class BudgetRequest(BaseModel):
    """預算設定請求"""

    monthly_budget: Optional[int] = Field(
        default=None, description="月預算金額（null 表示取消預算）", ge=0
    )


class BudgetResponse(BaseModel):
    """預算設定回應"""

    success: bool = True
    monthly_budget: Optional[int] = None
    message: str = ""


# =========================
# 錯誤相關
# =========================


class ErrorDetail(BaseModel):
    """錯誤詳情"""

    code: str = Field(..., description="錯誤代碼", example="PARSE_ERROR")
    message: str = Field(..., description="錯誤訊息", example="無法解析記帳內容")


class ErrorResponse(BaseModel):
    """錯誤回應"""

    success: bool = False
    error: ErrorDetail
