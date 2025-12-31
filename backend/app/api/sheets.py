"""用戶 Sheet 管理 API"""

import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.database.crud import (
    get_user_sheet,
    save_user_sheet,
    get_google_token,
    is_google_token_expired,
    save_google_token,
)
from app.services.user_sheets_service import create_user_sheets_service
from app.services.oauth_service import oauth_service
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# =========================
# 請求/回應模型
# =========================


class SheetInfo(BaseModel):
    """Sheet 資訊"""

    sheet_id: str
    sheet_url: str
    sheet_name: str


class DriveSheetItem(BaseModel):
    """Google Drive 中的 Sheet 項目"""

    id: str
    name: str
    modified_time: str
    url: str


class SheetResponse(BaseModel):
    """Sheet 回應"""

    success: bool = True
    sheet: Optional[SheetInfo] = None
    message: str


class DriveSheetListResponse(BaseModel):
    """Drive Sheet 列表回應"""

    success: bool = True
    sheets: List[DriveSheetItem] = []
    message: str


class CreateSheetRequest(BaseModel):
    """建立 Sheet 請求"""

    title: str = "語音記帳"


class SelectSheetRequest(BaseModel):
    """選擇 Sheet 請求"""

    sheet_id: str
    sheet_name: Optional[str] = None


# =========================
# API 端點
# =========================


@router.get("/list", response_model=DriveSheetListResponse)
async def list_drive_sheets(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    列出用戶 Google Drive 中的所有 Google Sheets

    需要 OAuth 登入
    """
    user_id = current_user.get("user_id")
    auth_type = current_user.get("auth_type")

    if auth_type != "jwt":
        raise HTTPException(status_code=403, detail="此功能需要 Google OAuth 登入")

    # 取得用戶的 Google Token
    google_token = await get_google_token(db, user_id)
    if not google_token:
        raise HTTPException(status_code=400, detail="找不到 Google Token，請重新登入")

    # 檢查並刷新 Token
    if await is_google_token_expired(google_token):
        if not google_token.refresh_token:
            raise HTTPException(status_code=400, detail="Token 已過期，請重新登入")

        try:
            new_access_token, new_expires_at = await oauth_service.refresh_access_token(
                google_token.refresh_token
            )
            google_token = await save_google_token(
                db,
                user_id=user_id,
                access_token=new_access_token,
                refresh_token=google_token.refresh_token,
                expires_at=new_expires_at,
            )
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(status_code=400, detail="Token 刷新失敗，請重新登入")

    # 列出所有 Sheets
    sheets_service = create_user_sheets_service(
        access_token=google_token.access_token,
        refresh_token=google_token.refresh_token,
        expires_at=google_token.expires_at,
    )

    try:
        drive_sheets = await sheets_service.list_all_sheets()
        sheets_list = [
            DriveSheetItem(
                id=s.id,
                name=s.name,
                modified_time=s.modified_time,
                url=f"https://docs.google.com/spreadsheets/d/{s.id}",
            )
            for s in drive_sheets
        ]

        return DriveSheetListResponse(
            success=True,
            sheets=sheets_list,
            message=f"找到 {len(sheets_list)} 個 Google Sheets",
        )

    except Exception as e:
        logger.error(f"List sheets failed: {e}")
        raise HTTPException(status_code=500, detail=f"列出 Sheets 失敗：{str(e)}")


@router.post("/select", response_model=SheetResponse)
async def select_sheet(
    request: SelectSheetRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    從清單中選擇一個 Google Sheet 作為記帳用

    需要 OAuth 登入
    """
    user_id = current_user.get("user_id")
    auth_type = current_user.get("auth_type")

    if auth_type != "jwt":
        raise HTTPException(status_code=403, detail="此功能需要 Google OAuth 登入")

    # 取得用戶的 Google Token
    google_token = await get_google_token(db, user_id)
    if not google_token:
        raise HTTPException(status_code=400, detail="找不到 Google Token，請重新登入")

    # 驗證是否可以存取該 Sheet
    sheets_service = create_user_sheets_service(
        access_token=google_token.access_token,
        refresh_token=google_token.refresh_token,
        expires_at=google_token.expires_at,
    )

    if not await sheets_service.verify_sheet_access(request.sheet_id):
        raise HTTPException(status_code=403, detail="無法存取該 Google Sheet")

    # 取得 Sheet 名稱（如果未提供）
    sheet_name = request.sheet_name
    if not sheet_name:
        sheet_name = await sheets_service.get_sheet_name(request.sheet_id)

    # 儲存 Sheet 資訊
    sheet_url = f"https://docs.google.com/spreadsheets/d/{request.sheet_id}"
    user_sheet = await save_user_sheet(
        db,
        user_id=user_id,
        sheet_id=request.sheet_id,
        sheet_url=sheet_url,
        sheet_name=sheet_name,
    )

    logger.info(f"Selected sheet for user {user_id}: {request.sheet_id}")

    return SheetResponse(
        success=True,
        sheet=SheetInfo(
            sheet_id=user_sheet.sheet_id,
            sheet_url=user_sheet.sheet_url,
            sheet_name=user_sheet.sheet_name,
        ),
        message="Sheet 選擇成功",
    )


@router.get("/my-sheet", response_model=SheetResponse)
async def get_my_sheet(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    取得當前用戶的 Sheet 資訊

    需要 OAuth 登入
    """
    user_id = current_user.get("user_id")
    auth_type = current_user.get("auth_type")

    if auth_type != "jwt":
        raise HTTPException(status_code=403, detail="此功能需要 Google OAuth 登入")

    user_sheet = await get_user_sheet(db, user_id)

    if not user_sheet:
        return SheetResponse(
            success=True,
            sheet=None,
            message="尚未建立 Sheet，請先建立",
        )

    return SheetResponse(
        success=True,
        sheet=SheetInfo(
            sheet_id=user_sheet.sheet_id,
            sheet_url=user_sheet.sheet_url,
            sheet_name=user_sheet.sheet_name,
        ),
        message="取得成功",
    )


@router.post("/create", response_model=SheetResponse)
async def create_sheet(
    request: CreateSheetRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    建立用戶專屬的 Google Sheet

    需要 OAuth 登入
    """
    user_id = current_user.get("user_id")
    auth_type = current_user.get("auth_type")

    if auth_type != "jwt":
        raise HTTPException(status_code=403, detail="此功能需要 Google OAuth 登入")

    # 檢查是否已有 Sheet
    existing_sheet = await get_user_sheet(db, user_id)
    if existing_sheet:
        return SheetResponse(
            success=True,
            sheet=SheetInfo(
                sheet_id=existing_sheet.sheet_id,
                sheet_url=existing_sheet.sheet_url,
                sheet_name=existing_sheet.sheet_name,
            ),
            message="已有現存的 Sheet",
        )

    # 取得用戶的 Google Token
    google_token = await get_google_token(db, user_id)
    if not google_token:
        raise HTTPException(status_code=400, detail="找不到 Google Token，請重新登入")

    # 檢查並刷新 Token
    if await is_google_token_expired(google_token):
        if not google_token.refresh_token:
            raise HTTPException(status_code=400, detail="Token 已過期，請重新登入")

        try:
            new_access_token, new_expires_at = await oauth_service.refresh_access_token(
                google_token.refresh_token
            )
            google_token = await save_google_token(
                db,
                user_id=user_id,
                access_token=new_access_token,
                refresh_token=google_token.refresh_token,
                expires_at=new_expires_at,
            )
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(status_code=400, detail="Token 刷新失敗，請重新登入")

    # 建立 Sheet
    sheets_service = create_user_sheets_service(
        access_token=google_token.access_token,
        refresh_token=google_token.refresh_token,
        expires_at=google_token.expires_at,
    )

    try:
        sheet_id, sheet_url = await sheets_service.create_sheet(title=request.title)

        # 儲存 Sheet 資訊
        user_sheet = await save_user_sheet(
            db,
            user_id=user_id,
            sheet_id=sheet_id,
            sheet_url=sheet_url,
            sheet_name="記帳紀錄",
        )

        logger.info(f"Created sheet for user {user_id}: {sheet_id}")

        return SheetResponse(
            success=True,
            sheet=SheetInfo(
                sheet_id=user_sheet.sheet_id,
                sheet_url=user_sheet.sheet_url,
                sheet_name=user_sheet.sheet_name,
            ),
            message="Sheet 建立成功",
        )

    except Exception as e:
        logger.error(f"Create sheet failed: {e}")
        raise HTTPException(status_code=500, detail=f"建立 Sheet 失敗：{str(e)}")


@router.post("/link")
async def link_sheet(
    sheet_url: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    連結現有的 Google Sheet

    需要 OAuth 登入
    """
    user_id = current_user.get("user_id")
    auth_type = current_user.get("auth_type")

    if auth_type != "jwt":
        raise HTTPException(status_code=403, detail="此功能需要 Google OAuth 登入")

    # 從 URL 提取 Sheet ID
    # 格式：https://docs.google.com/spreadsheets/d/{SHEET_ID}/...
    try:
        parts = sheet_url.split("/d/")
        if len(parts) < 2:
            raise ValueError("Invalid URL format")
        sheet_id = parts[1].split("/")[0]
    except Exception:
        raise HTTPException(status_code=400, detail="無效的 Google Sheet URL")

    # 取得用戶的 Google Token
    google_token = await get_google_token(db, user_id)
    if not google_token:
        raise HTTPException(status_code=400, detail="找不到 Google Token，請重新登入")

    # 驗證是否可以存取該 Sheet
    sheets_service = create_user_sheets_service(
        access_token=google_token.access_token,
        refresh_token=google_token.refresh_token,
        expires_at=google_token.expires_at,
    )

    if not await sheets_service.verify_sheet_access(sheet_id):
        raise HTTPException(status_code=403, detail="無法存取該 Google Sheet")

    # 儲存 Sheet 資訊
    user_sheet = await save_user_sheet(
        db,
        user_id=user_id,
        sheet_id=sheet_id,
        sheet_url=sheet_url,
        sheet_name="記帳紀錄",
    )

    logger.info(f"Linked sheet for user {user_id}: {sheet_id}")

    return SheetResponse(
        success=True,
        sheet=SheetInfo(
            sheet_id=user_sheet.sheet_id,
            sheet_url=user_sheet.sheet_url,
            sheet_name=user_sheet.sheet_name,
        ),
        message="Sheet 連結成功",
    )
