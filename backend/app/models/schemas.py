"""Pydantic 資料模型"""

from typing import Optional
from pydantic import BaseModel


class AccountingRequest(BaseModel):
    """記帳請求"""

    text: str  # 語音轉文字內容，如 "中午吃排骨便當120元"


class AccountingRecord(BaseModel):
    """記帳記錄"""

    時間: str
    名稱: str
    類別: str
    花費: float
    幣別: str = "TWD"
    支付方式: Optional[str] = None


class AccountingResponse(BaseModel):
    """記帳回應"""

    success: bool
    record: AccountingRecord
    message: str


class ErrorResponse(BaseModel):
    """錯誤回應"""

    success: bool = False
    error: dict
