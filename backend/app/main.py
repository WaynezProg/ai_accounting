"""FastAPI 應用程式入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import health, accounting

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

# 註冊路由
app.include_router(health.router, tags=["Health"])
app.include_router(accounting.router, prefix="/api/accounting", tags=["Accounting"])


@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "語音記帳助手 API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENV == "development",
    )
