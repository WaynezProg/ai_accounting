"""應用程式設定"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """環境變數設定"""

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENV: str = os.getenv("ENV", "development")

    # CORS
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    # GOOGLE_REDIRECT_URI 已棄用，改為動態產生：FRONTEND_URL + GOOGLE_OAUTH_CALLBACK_PATH
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")  # deprecated
    GOOGLE_OAUTH_CALLBACK_PATH: str = os.getenv(
        "GOOGLE_OAUTH_CALLBACK_PATH", "/auth/google/callback"
    )
    GOOGLE_OAUTH_SCOPES: list = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",  # 讀取所有 Drive 檔案列表
    ]

    # JWT
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "change-this-secret-key-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "15"))
    JWT_REFRESH_EXPIRE_HOURS: int = int(
        os.getenv("JWT_REFRESH_EXPIRE_HOURS", "168")
    )  # 7 days
    JWT_REFRESH_INACTIVITY_HOURS: int = int(
        os.getenv("JWT_REFRESH_INACTIVITY_HOURS", "48")
    )
    JWT_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_EXPIRE_MINUTES", "1440")
    )  # 24 hours (legacy)

    # OAuth one-time code
    OAUTH_CODE_EXPIRE_MINUTES: int = int(os.getenv("OAUTH_CODE_EXPIRE_MINUTES", "5"))

    # Frontend URL (for OAuth redirect)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")


settings = Settings()
