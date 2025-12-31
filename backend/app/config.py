"""應用程式設定"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """環境變數設定"""

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

    # Google Sheets (Service Account)
    GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_FILE", "./credentials/service-account.json"
    )
    GOOGLE_SHEET_URL: str = os.getenv("GOOGLE_SHEET_URL", "")
    GOOGLE_SHEET_WORKSHEET: str = os.getenv("GOOGLE_SHEET_WORKSHEET", "記帳")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENV: str = os.getenv("ENV", "development")

    # CORS
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",")


settings = Settings()
