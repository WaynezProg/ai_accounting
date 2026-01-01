"""用戶專屬 Google Sheets 服務

使用用戶的 OAuth Token 操作其專屬的 Google Sheet
"""

import logging
import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings
from app.models.schemas import AccountingRecord, MonthlyStats

logger = logging.getLogger(__name__)


class GoogleSheetsError(Exception):
    """Google Sheets 操作錯誤"""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


# Sheet 標題列
SHEET_HEADERS = ["時間", "名稱", "類別", "花費", "幣別", "支付方式"]


class DriveSheetInfo:
    """Google Drive 中的 Sheet 資訊"""

    def __init__(self, id: str, name: str, modified_time: str):
        self.id = id
        self.name = name
        self.modified_time = modified_time

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "modified_time": self.modified_time,
            "url": f"https://docs.google.com/spreadsheets/d/{self.id}",
        }


class UserSheetsService:
    """用戶專屬 Google Sheets 服務（OAuth 模式）"""

    def __init__(self, credentials: Credentials):
        """
        初始化服務

        Args:
            credentials: 用戶的 Google OAuth Credentials
        """
        self.credentials = credentials
        self._sheets_service = None
        self._drive_service = None

    @property
    def sheets_service(self):
        """取得 Google Sheets API 服務"""
        if self._sheets_service is None:
            self._sheets_service = build("sheets", "v4", credentials=self.credentials)
        return self._sheets_service

    @property
    def drive_service(self):
        """取得 Google Drive API 服務"""
        if self._drive_service is None:
            self._drive_service = build("drive", "v3", credentials=self.credentials)
        return self._drive_service

    async def list_all_sheets(self, page_size: int = 100) -> List[DriveSheetInfo]:
        """
        列出用戶 Google Drive 中的所有 Google Sheets

        Args:
            page_size: 每頁數量（最大 1000）

        Returns:
            List[DriveSheetInfo]: Sheet 列表
        """
        try:
            sheets = []
            page_token = None

            while True:
                # 查詢 Google Sheets 類型的檔案
                response = (
                    self.drive_service.files()
                    .list(
                        q="mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
                        spaces="drive",
                        fields="nextPageToken, files(id, name, modifiedTime)",
                        pageSize=page_size,
                        pageToken=page_token,
                        orderBy="modifiedTime desc",
                    )
                    .execute()
                )

                for file in response.get("files", []):
                    sheets.append(
                        DriveSheetInfo(
                            id=file["id"],
                            name=file["name"],
                            modified_time=file["modifiedTime"],
                        )
                    )

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            logger.info(f"Listed {len(sheets)} sheets from Drive")
            return sheets

        except HttpError as e:
            logger.error(f"List sheets failed: {e}")
            raise GoogleSheetsError("LIST_ERROR", f"列出 Google Sheets 失敗：{str(e)}")

    async def get_sheet_name(self, sheet_id: str) -> str:
        """
        取得 Sheet 的名稱

        Args:
            sheet_id: Google Sheet ID

        Returns:
            str: Sheet 名稱
        """
        try:
            result = (
                self.sheets_service.spreadsheets()
                .get(spreadsheetId=sheet_id, fields="properties.title")
                .execute()
            )
            return result.get("properties", {}).get("title", "未命名")
        except HttpError as e:
            logger.error(f"Get sheet name failed: {e}")
            return "未命名"

    async def create_sheet(self, title: str = "語音記帳") -> tuple[str, str]:
        """
        建立新的 Google Sheet

        Args:
            title: Sheet 標題

        Returns:
            (sheet_id, sheet_url)
        """
        try:
            # 取得當月分頁名稱
            current_month = datetime.now().strftime("%Y-%m")

            # 建立新試算表，使用當月作為第一個分頁
            spreadsheet = {
                "properties": {"title": title},
                "sheets": [
                    {
                        "properties": {
                            "title": current_month,
                            "gridProperties": {"rowCount": 1000, "columnCount": 10},
                        }
                    }
                ],
            }

            result = (
                self.sheets_service.spreadsheets()
                .create(body=spreadsheet, fields="spreadsheetId,spreadsheetUrl")
                .execute()
            )

            sheet_id = result.get("spreadsheetId")
            sheet_url = result.get("spreadsheetUrl")

            logger.info(f"Created new sheet: {sheet_id}")

            # 初始化當月分頁的標題列
            await self._init_worksheet_headers(sheet_id, current_month)

            return sheet_id, sheet_url

        except HttpError as e:
            logger.error(f"Create sheet failed: {e}")
            raise GoogleSheetsError("CREATE_ERROR", f"建立 Google Sheet 失敗：{str(e)}")

    async def _get_worksheets(self, sheet_id: str) -> List[str]:
        """
        取得 Sheet 中所有工作表（分頁）的名稱

        Args:
            sheet_id: Google Sheet ID

        Returns:
            List[str]: 工作表名稱列表
        """
        try:
            result = (
                self.sheets_service.spreadsheets()
                .get(spreadsheetId=sheet_id, fields="sheets.properties.title")
                .execute()
            )
            sheets = result.get("sheets", [])
            return [s["properties"]["title"] for s in sheets]
        except HttpError as e:
            logger.error(f"Get worksheets failed: {e}")
            return []

    async def _create_worksheet(self, sheet_id: str, worksheet_name: str) -> bool:
        """
        在 Sheet 中建立新的工作表（分頁）

        Args:
            sheet_id: Google Sheet ID
            worksheet_name: 工作表名稱（如 "2024-01"）

        Returns:
            bool: 是否成功
        """
        try:
            request = {
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": worksheet_name,
                                "gridProperties": {"rowCount": 1000, "columnCount": 10},
                            }
                        }
                    }
                ]
            }
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body=request
            ).execute()

            # 初始化標題列
            await self._init_worksheet_headers(sheet_id, worksheet_name)

            logger.info(f"Created worksheet '{worksheet_name}' in sheet {sheet_id}")
            return True

        except HttpError as e:
            logger.error(f"Create worksheet failed: {e}")
            return False

    async def _init_worksheet_headers(self, sheet_id: str, worksheet_name: str):
        """初始化工作表的標題列"""
        try:
            body = {"values": [SHEET_HEADERS]}
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"'{worksheet_name}'!A1",
                valueInputOption="RAW",
                body=body,
            ).execute()
            logger.info(f"Initialized headers for worksheet: {worksheet_name}")
        except HttpError as e:
            logger.error(f"Init worksheet headers failed: {e}")
            raise GoogleSheetsError("INIT_ERROR", f"初始化標題列失敗：{str(e)}")

    async def _ensure_worksheet_exists(self, sheet_id: str, month: str) -> str:
        """
        確保月份對應的工作表存在，不存在則建立

        Args:
            sheet_id: Google Sheet ID
            month: 月份（格式：YYYY-MM）

        Returns:
            str: 工作表名稱
        """
        worksheets = await self._get_worksheets(sheet_id)

        if month not in worksheets:
            logger.info(f"Worksheet '{month}' not found, creating...")
            await self._create_worksheet(sheet_id, month)

        return month

    def _extract_month_from_time(self, time_str: str) -> str:
        """
        從時間字串中提取月份

        Args:
            time_str: 時間字串（如 "2024-01-15 14:30"）

        Returns:
            str: 月份（如 "2024-01"）
        """
        # 嘗試匹配 YYYY-MM 格式
        match = re.match(r"(\d{4}-\d{2})", time_str)
        if match:
            return match.group(1)
        # 預設返回當月
        return datetime.now().strftime("%Y-%m")

    async def write_record(self, sheet_id: str, record: AccountingRecord) -> bool:
        """
        寫入記帳記錄到對應的月份分頁

        Args:
            sheet_id: Google Sheet ID
            record: 記帳記錄

        Returns:
            bool: 是否成功
        """
        try:
            # 從記錄的時間提取月份
            month = self._extract_month_from_time(record.時間)

            # 確保月份分頁存在
            worksheet_name = await self._ensure_worksheet_exists(sheet_id, month)

            # 準備寫入資料
            values = [
                [
                    record.時間,
                    record.名稱,
                    record.類別,
                    record.花費,
                    record.幣別,
                    record.支付方式 or "",
                ]
            ]

            body = {"values": values}

            # 使用 append 自動找到下一行，寫入對應月份的分頁
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"'{worksheet_name}'!A:F",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            ).execute()

            logger.info(f"Written record to sheet {sheet_id}/{worksheet_name}: {record.名稱}")
            return True

        except HttpError as e:
            logger.error(f"Write record failed: {e}")
            raise GoogleSheetsError("WRITE_ERROR", f"寫入 Google Sheet 失敗：{str(e)}")

    async def get_all_records(
        self, sheet_id: str, month: Optional[str] = None
    ) -> List[Dict]:
        """
        讀取記帳記錄

        Args:
            sheet_id: Google Sheet ID
            month: 月份（格式：YYYY-MM），如果未提供則讀取所有分頁

        Returns:
            list: 記帳記錄列表
        """
        try:
            all_records = []

            if month:
                # 只讀取指定月份的分頁
                worksheets = [month]
            else:
                # 讀取所有分頁
                worksheets = await self._get_worksheets(sheet_id)

            for worksheet in worksheets:
                try:
                    result = (
                        self.sheets_service.spreadsheets()
                        .values()
                        .get(spreadsheetId=sheet_id, range=f"'{worksheet}'!A:F")
                        .execute()
                    )

                    values = result.get("values", [])

                    if len(values) <= 1:  # 只有標題或沒有資料
                        continue

                    # 轉換為 dict 列表（跳過標題列）
                    headers = values[0]
                    for row in values[1:]:
                        # 補齊缺少的欄位
                        while len(row) < len(headers):
                            row.append("")
                        all_records.append(dict(zip(headers, row)))

                except HttpError as e:
                    # 某個分頁讀取失敗不影響其他分頁
                    logger.warning(f"Failed to read worksheet '{worksheet}': {e}")
                    continue

            return all_records

        except HttpError as e:
            logger.error(f"Get all records failed: {e}")
            raise GoogleSheetsError("READ_ERROR", f"讀取 Google Sheet 失敗：{str(e)}")

    async def get_monthly_stats(
        self, sheet_id: str, month: Optional[str] = None
    ) -> MonthlyStats:
        """
        取得月度統計資料

        直接讀取對應月份的分頁，效能更好

        Args:
            sheet_id: Google Sheet ID
            month: 月份（格式：YYYY-MM），如果未提供則使用當月

        Returns:
            MonthlyStats: 月度統計
        """
        try:
            # 預設使用當月
            if month is None:
                month = datetime.now().strftime("%Y-%m")

            # 直接讀取該月份的分頁
            records = await self.get_all_records(sheet_id, month=month)

            if not records:
                return MonthlyStats(
                    month=month,
                    total=0.0,
                    record_count=0,
                    by_category={},
                )

            # 計算統計
            total = 0.0
            by_category: Dict[str, float] = {}

            for record in records:
                try:
                    amount = float(record.get("花費", 0))
                    total += amount

                    category = record.get("類別", "其他")
                    by_category[category] = by_category.get(category, 0) + amount
                except (ValueError, TypeError):
                    continue

            logger.info(
                f"Monthly stats for {month}: total={total}, count={len(records)}"
            )

            return MonthlyStats(
                month=month,
                total=total,
                record_count=len(records),
                by_category=by_category,
            )

        except Exception as e:
            logger.error(f"Get monthly stats failed: {e}")
            raise GoogleSheetsError("STATS_ERROR", f"統計查詢失敗：{str(e)}")

    async def verify_sheet_access(self, sheet_id: str) -> bool:
        """
        驗證是否可以存取指定的 Sheet

        Args:
            sheet_id: Google Sheet ID

        Returns:
            bool: 是否可以存取
        """
        try:
            self.sheets_service.spreadsheets().get(
                spreadsheetId=sheet_id, fields="spreadsheetId"
            ).execute()
            return True
        except HttpError:
            return False


def create_user_sheets_service(
    access_token: str,
    refresh_token: Optional[str] = None,
    expires_at: Optional[datetime] = None,
) -> UserSheetsService:
    """
    建立用戶專屬 Sheets 服務的便利函數

    Args:
        access_token: Google Access Token
        refresh_token: Google Refresh Token
        expires_at: Token 過期時間

    Returns:
        UserSheetsService 實例
    """
    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        expiry=expires_at,
    )

    return UserSheetsService(credentials)
