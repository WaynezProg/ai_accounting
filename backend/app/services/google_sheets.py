"""Google Sheets 服務"""

import logging
from datetime import datetime
from typing import Optional, List, Dict

import pandas as pd
import pygsheets

from app.config import settings
from app.models.schemas import AccountingRecord, MonthlyStats

logger = logging.getLogger(__name__)


class GoogleSheetsError(Exception):
    """Google Sheets 服務錯誤"""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class GoogleSheetsService:
    """Google Sheets 服務類別（Service Account 模式）"""

    def __init__(self):
        self._client = None
        self._sheet = None

    def _get_client(self):
        """取得 Google Sheets 客戶端（延遲初始化）"""
        if self._client is None:
            self._client = pygsheets.authorize(
                service_file=settings.GOOGLE_SERVICE_ACCOUNT_FILE
            )
        return self._client

    def _get_worksheet(self):
        """取得工作表"""
        if self._sheet is None:
            client = self._get_client()
            spreadsheet = client.open_by_url(settings.GOOGLE_SHEET_URL)
            self._sheet = spreadsheet.worksheet_by_title(settings.GOOGLE_SHEET_WORKSHEET)
        return self._sheet

    async def write_record(self, record: AccountingRecord) -> bool:
        """
        寫入記帳記錄到 Google Sheets

        Args:
            record: 記帳記錄

        Returns:
            bool: 是否成功
        """
        try:
            sheet = self._get_worksheet()

            # 取得現有資料行數
            df = sheet.get_as_df()
            start_row = len(df) + 2  # +2 因為有標題列，且從 1 開始

            # 準備寫入資料
            row_data = [
                [
                    record.時間,
                    record.名稱,
                    record.類別,
                    record.花費,
                    record.幣別,
                    record.支付方式 or "",
                ]
            ]

            # 寫入資料
            sheet.update_values(crange=f"A{start_row}", values=row_data)
            logger.info(f"Written record to row {start_row}: {record.名稱}")

            return True

        except pygsheets.SpreadsheetNotFound:
            raise GoogleSheetsError("SHEET_NOT_FOUND", "無法找到指定的 Google Sheet")
        except pygsheets.WorksheetNotFound:
            raise GoogleSheetsError(
                "WORKSHEET_NOT_FOUND", f"無法找到工作表：{settings.GOOGLE_SHEET_WORKSHEET}"
            )
        except Exception as e:
            logger.error(f"Write record failed: {e}")
            raise GoogleSheetsError("WRITE_ERROR", f"寫入 Google Sheets 失敗：{str(e)}")

    async def get_all_records(self) -> List[Dict]:
        """
        讀取所有記帳記錄

        Returns:
            list: 記帳記錄列表
        """
        try:
            sheet = self._get_worksheet()
            df = sheet.get_as_df()

            if df.empty:
                return []

            return df.to_dict("records")

        except Exception as e:
            logger.error(f"Get all records failed: {e}")
            raise GoogleSheetsError("READ_ERROR", f"讀取 Google Sheets 失敗：{str(e)}")

    async def get_monthly_stats(self, month: Optional[str] = None) -> MonthlyStats:
        """
        取得月度統計資料

        Args:
            month: 月份（格式：YYYY-MM），如果未提供則使用當月

        Returns:
            MonthlyStats: 月度統計
        """
        try:
            # 預設使用當月
            if month is None:
                month = datetime.now().strftime("%Y-%m")

            records = await self.get_all_records()

            if not records:
                return MonthlyStats(
                    month=month,
                    total=0.0,
                    record_count=0,
                    by_category={},
                )

            # 轉換為 DataFrame 進行處理
            df = pd.DataFrame(records)

            # 確保花費欄位為數字
            df["花費"] = pd.to_numeric(df["花費"], errors="coerce").fillna(0)

            # 篩選指定月份的記錄
            # 時間格式：YYYY-MM-DD HH:MM
            df["月份"] = df["時間"].str[:7]
            monthly_df = df[df["月份"] == month]

            if monthly_df.empty:
                return MonthlyStats(
                    month=month,
                    total=0.0,
                    record_count=0,
                    by_category={},
                )

            # 計算統計
            total = float(monthly_df["花費"].sum())
            record_count = len(monthly_df)

            # 各類別統計
            by_category = monthly_df.groupby("類別")["花費"].sum().to_dict()
            # 轉換為 float（確保 JSON 序列化）
            by_category = {k: float(v) for k, v in by_category.items()}

            logger.info(f"Monthly stats for {month}: total={total}, count={record_count}")

            return MonthlyStats(
                month=month,
                total=total,
                record_count=record_count,
                by_category=by_category,
            )

        except Exception as e:
            logger.error(f"Get monthly stats failed: {e}")
            raise GoogleSheetsError("STATS_ERROR", f"統計查詢失敗：{str(e)}")

    async def init_sheet(self) -> bool:
        """
        初始化工作表結構（建立標題列）

        Returns:
            bool: 是否成功
        """
        try:
            sheet = self._get_worksheet()

            # 檢查是否已有標題
            first_row = sheet.get_row(1)
            if first_row and first_row[0]:
                logger.info("Sheet already initialized")
                return True

            # 建立標題列
            headers = [["時間", "名稱", "類別", "花費", "幣別", "支付方式"]]
            sheet.update_values(crange="A1", values=headers)
            logger.info("Sheet initialized with headers")

            return True

        except Exception as e:
            logger.error(f"Init sheet failed: {e}")
            raise GoogleSheetsError("INIT_ERROR", f"初始化工作表失敗：{str(e)}")


# 單例模式
google_sheets_service = GoogleSheetsService()
