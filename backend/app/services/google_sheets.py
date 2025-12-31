"""Google Sheets 服務"""

import pygsheets

from app.config import settings
from app.models.schemas import AccountingRecord


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

            return True

        except pygsheets.SpreadsheetNotFound:
            raise Exception("無法找到指定的 Google Sheet")
        except pygsheets.WorksheetNotFound:
            raise Exception(f"無法找到工作表：{settings.GOOGLE_SHEET_WORKSHEET}")
        except Exception as e:
            raise Exception(f"寫入 Google Sheets 失敗：{str(e)}")

    async def get_all_records(self) -> list:
        """
        讀取所有記帳記錄

        Returns:
            list: 記帳記錄列表
        """
        try:
            sheet = self._get_worksheet()
            df = sheet.get_as_df()
            return df.to_dict("records")
        except Exception as e:
            raise Exception(f"讀取 Google Sheets 失敗：{str(e)}")

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
                return True  # 已有資料，不需初始化

            # 建立標題列
            headers = [["時間", "名稱", "類別", "花費", "幣別", "支付方式"]]
            sheet.update_values(crange="A1", values=headers)

            return True

        except Exception as e:
            raise Exception(f"初始化工作表失敗：{str(e)}")


# 單例模式
google_sheets_service = GoogleSheetsService()
