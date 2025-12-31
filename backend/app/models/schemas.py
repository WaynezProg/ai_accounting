"""Pydantic 資料模型"""

from typing import Optional, Dict, Any
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
    支付方式: Optional[str] = Field(default=None, description="支付方式", example="現金")


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


class StatsResponse(BaseModel):
    """統計回應"""

    success: bool = True
    data: MonthlyStats


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
