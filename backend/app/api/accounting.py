"""記帳 API 端點"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import AccountingRequest, AccountingResponse
from app.services.openai_service import openai_service
from app.services.google_sheets import google_sheets_service
from app.utils.categories import DEFAULT_CATEGORIES

router = APIRouter()


@router.post("/record", response_model=AccountingResponse)
async def record_accounting(request: AccountingRequest):
    """
    記帳端點

    接收語音轉文字內容，使用 LLM 解析後寫入 Google Sheets
    """
    try:
        # 1. 使用 LLM 解析記帳文字
        record = await openai_service.parse_accounting_text(request.text)

        # 2. 寫入 Google Sheets
        await google_sheets_service.write_record(record)

        # 3. 回傳結果
        return AccountingResponse(
            success=True,
            record=record,
            message=f"已記錄：{record.名稱} {record.花費}{record.幣別}",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """取得預設類別清單"""
    return {
        "success": True,
        "categories": DEFAULT_CATEGORIES,
    }
