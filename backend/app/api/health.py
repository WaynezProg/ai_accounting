"""健康檢查 API"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "service": "ai-accounting",
    }
