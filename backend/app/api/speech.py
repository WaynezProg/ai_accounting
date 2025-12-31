"""語音服務 API 端點"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.services.openai_service import openai_service
from app.utils.auth import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()


class TTSRequest(BaseModel):
    """TTS 請求"""

    text: str = Field(..., description="要轉換的文字", max_length=4096)
    voice: Optional[str] = Field(
        default="nova",
        description="聲音選擇：alloy, echo, fable, onyx, nova, shimmer",
    )
    speed: Optional[float] = Field(
        default=1.0,
        description="語速，範圍 0.25 到 4.0",
        ge=0.25,
        le=4.0,
    )


@router.post("/synthesize")
async def synthesize_speech(
    request: TTSRequest,
    token_valid: bool = Depends(verify_token),
):
    """
    文字轉語音 (TTS)

    使用 OpenAI TTS API 將文字轉換為自然語音

    需要在 Authorization header 提供 Bearer Token

    Returns:
        音訊檔案 (MP3 格式)
    """
    logger.info(f"TTS request: {request.text[:50]}...")

    try:
        audio_data = await openai_service.text_to_speech(
            text=request.text,
            voice=request.voice or "nova",
            speed=request.speed or 1.0,
        )

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
            },
        )

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"語音合成失敗: {str(e)}")


@router.get("/voices")
async def get_available_voices():
    """
    取得可用的聲音列表

    此端點不需要認證
    """
    return {
        "success": True,
        "voices": [
            {"id": "alloy", "name": "Alloy", "description": "中性、平衡"},
            {"id": "ash", "name": "Ash", "description": "中性、沉穩"},
            {"id": "ballad", "name": "Ballad", "description": "抒情、溫柔"},
            {"id": "coral", "name": "Coral", "description": "女性、清晰"},
            {"id": "echo", "name": "Echo", "description": "男性、沉穩"},
            {"id": "fable", "name": "Fable", "description": "英式、敘事感"},
            {"id": "onyx", "name": "Onyx", "description": "男性、深沉"},
            {"id": "nova", "name": "Nova", "description": "女性、自然友善（推薦中文）"},
            {"id": "sage", "name": "Sage", "description": "中性、穩重"},
            {"id": "shimmer", "name": "Shimmer", "description": "女性、清晰表達"},
            {"id": "verse", "name": "Verse", "description": "中性、自然"},
        ],
    }
