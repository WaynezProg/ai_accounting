"""FastAPI 應用程式入口"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api import health, accounting, auth, speech, sheets
from app.database import init_db, close_db
from app.utils.exceptions import AppException
from app.services.openai_service import OpenAIServiceError
from app.services.google_sheets import GoogleSheetsError

# 設定日誌
logging.basicConfig(
    level=logging.INFO if settings.ENV == "development" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="語音記帳助手 API",
    description="整合 Siri 捷徑、LLM 和 Google Sheets 的記帳系統",
    version="0.1.0",
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# 全域錯誤處理器
# =========================


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """處理應用程式自訂例外"""
    logger.warning(f"AppException: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


@app.exception_handler(OpenAIServiceError)
async def openai_exception_handler(request: Request, exc: OpenAIServiceError):
    """處理 OpenAI 服務錯誤"""
    logger.error(f"OpenAIServiceError: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=502,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


@app.exception_handler(GoogleSheetsError)
async def sheets_exception_handler(request: Request, exc: GoogleSheetsError):
    """處理 Google Sheets 服務錯誤"""
    logger.error(f"GoogleSheetsError: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=502,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """處理未預期的例外"""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "伺服器內部錯誤",
            },
        },
    )


# =========================
# 路由註冊
# =========================

app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(accounting.router, prefix="/api/accounting", tags=["Accounting"])
app.include_router(speech.router, prefix="/api/speech", tags=["Speech"])
app.include_router(sheets.router, prefix="/api/sheets", tags=["Sheets"])


@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "語音記帳助手 API",
        "version": "0.1.0",
        "docs": "/docs",
    }


# =========================
# 啟動事件
# =========================


@app.on_event("startup")
async def startup_event():
    """應用程式啟動時執行"""
    logger.info(f"Starting server in {settings.ENV} mode")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")

    # 初始化資料庫
    await init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """應用程式關閉時執行"""
    await close_db()
    logger.info("Database connection closed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENV == "development",
    )
