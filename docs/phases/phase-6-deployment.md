# Phase 6：部署上線 ✅ 已完成

## 目標

將應用部署至雲端，採用 **Cloud Run + Turso + Vercel** 架構。

---

## 部署資訊

| 服務 | URL | 狀態 |
|------|-----|------|
| **後端 API (Cloud Run)** | https://ai-accounting-api-51386650140.asia-east1.run.app | ✅ 運作中 |
| **前端 (Vercel)** | https://frontend-omega-eight-30.vercel.app | ✅ 運作中 |
| **資料庫 (Turso)** | libsql://ai-accounting-waynezprog.aws-ap-northeast-1.turso.io | ✅ 運作中 |

---

## 部署架構

```
┌─────────────────────────────────────────────────────────────────┐
│                         使用者                                   │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│      Vercel (前端)           │   │    iPhone Siri 捷徑         │
│   - React SPA               │   │                             │
│   - 全球 CDN                 │   │                             │
│   - 免費方案                 │   │                             │
└─────────────────────────────┘   └─────────────────────────────┘
                    │                           │
                    └───────────┬───────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              GCP Cloud Run (後端 API)                            │
│   - FastAPI                                                      │
│   - asia-east1 (台灣彰化)                                        │
│   - 低延遲 (~5-10ms)                                            │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Turso         │  │   OpenAI API    │  │  Google APIs    │
│   (libSQL)      │  │   (LLM + TTS)   │  │  (Sheets/OAuth) │
│   邊緣節點       │  │                 │  │                 │
│   免費方案       │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 成本估算

| 服務 | 方案 | 月費 USD | 月費 TWD |
|------|------|----------|----------|
| Cloud Run | 免費額度 | ~$0-5 | ~0-160 |
| Turso | Free | $0 | 0 |
| Vercel | Hobby | $0 | 0 |
| OpenAI API | 用量計費 | ~$2-6 | ~64-192 |
| **總計** | | **~$2-11** | **~64-352** |

---

## 任務清單

### 6.1 Turso 設定 ✅

- [x] 建立 Turso 帳號與資料庫
  ```bash
  # 安裝 Turso CLI
  brew install tursodatabase/tap/turso

  # 登入
  turso auth login

  # 建立資料庫
  turso db create ai-accounting
  ```

- [x] 取得連線資訊
  ```bash
  # 取得資料庫 URL
  turso db show ai-accounting --url
  # 輸出：libsql://ai-accounting-waynezprog.aws-ap-northeast-1.turso.io

  # 建立 Token
  turso db tokens create ai-accounting
  ```

- [x] 連線資訊
  - `TURSO_DATABASE_URL`：`libsql://ai-accounting-waynezprog.aws-ap-northeast-1.turso.io`
  - `TURSO_AUTH_TOKEN`：已儲存至 GCP Secret Manager

### 6.2 後端程式碼調整 ✅

- [x] 安裝 Turso driver
  ```bash
  pip install sqlalchemy-libsql
  ```

- [x] 更新 `requirements.txt`
  ```
  # Database
  sqlalchemy==2.0.45

  # Turso driver (Phase 6 - Production)
  sqlalchemy-libsql==0.2.0
  ```

- [x] 更新 `backend/app/database/engine.py`

  **重要變更**：從 async 改為 sync 操作，因為 `sqlalchemy-libsql` 不支援 async。

  ```python
  """資料庫引擎設定

  支援兩種資料庫模式：
  1. Turso (生產環境)：使用 sqlalchemy-libsql
  2. SQLite (本地開發)：使用標準 sqlite

  統一使用同步 Session 以簡化程式碼。
  """

  import logging
  import os
  from typing import Generator
  from pathlib import Path

  from sqlalchemy import create_engine
  from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

  from app.config import settings

  logger = logging.getLogger(__name__)


  class Base(DeclarativeBase):
      """SQLAlchemy 基礎類別"""
      pass


  def is_turso_enabled() -> bool:
      """檢查是否啟用 Turso"""
      turso_url = os.getenv("TURSO_DATABASE_URL")
      turso_token = os.getenv("TURSO_AUTH_TOKEN")
      return bool(turso_url and turso_token)


  def get_turso_config() -> tuple[str, str]:
      """取得 Turso 設定"""
      turso_url = os.getenv("TURSO_DATABASE_URL", "")
      turso_token = os.getenv("TURSO_AUTH_TOKEN", "")
      # 移除 libsql:// 前綴，因為 sqlalchemy-libsql 格式是 sqlite+libsql://host
      host = turso_url.replace("libsql://", "")
      return host, turso_token


  def get_sqlite_url() -> str:
      """取得本地 SQLite URL"""
      DATABASE_DIR = Path(__file__).parent.parent.parent / "data"
      DATABASE_DIR.mkdir(exist_ok=True)
      return f"sqlite:///{DATABASE_DIR}/app.db"


  # 判斷使用哪種資料庫
  USE_TURSO = is_turso_enabled()

  if USE_TURSO:
      # Turso：使用 sqlalchemy-libsql
      turso_host, turso_token = get_turso_config()
      DATABASE_URL = f"sqlite+libsql://{turso_host}?secure=true"
      logger.info(f"Using Turso database: {turso_host}")

      engine = create_engine(
          DATABASE_URL,
          echo=settings.ENV == "development",
          connect_args={"auth_token": turso_token},
      )
  else:
      # 本地開發：使用同步 SQLite
      DATABASE_URL = get_sqlite_url()
      logger.info(f"Using local SQLite database: {DATABASE_URL}")

      engine = create_engine(
          DATABASE_URL,
          echo=settings.ENV == "development",
          connect_args={"check_same_thread": False},
      )

  # 統一使用同步 Session 工廠
  SessionLocal = sessionmaker(
      engine,
      class_=Session,
      expire_on_commit=False,
  )


  def init_db() -> None:
      """初始化資料庫（建立表格）"""
      from app.database import models  # noqa: F401
      Base.metadata.create_all(engine)
      logger.info("Database initialized")


  def close_db() -> None:
      """關閉資料庫連線"""
      engine.dispose()
      logger.info("Database connection closed")


  def get_db() -> Generator[Session, None, None]:
      """取得資料庫 Session（用於 FastAPI Depends）"""
      session = SessionLocal()
      try:
          yield session
      finally:
          session.close()
  ```

- [x] 更新相關檔案（移除 async/await）
  - `backend/app/database/crud.py` - 所有函數改為同步
  - `backend/app/api/auth.py` - `AsyncSession` → `Session`
  - `backend/app/api/accounting.py` - `AsyncSession` → `Session`
  - `backend/app/api/sheets.py` - `AsyncSession` → `Session`
  - `backend/app/utils/auth.py` - async 函數改為同步
  - `backend/app/main.py` - `init_db()` 和 `close_db()` 不再使用 await

### 6.3 GCP Cloud Run 部署 ✅

- [x] GCP 專案設定
  - 專案 ID：`ai-accounting-482914`
  - 區域：`asia-east1`（台灣彰化）
  - Billing 已啟用
  - Cloud Run API 已啟用
  - Secret Manager API 已啟用

- [x] `backend/Dockerfile`
  ```dockerfile
  FROM python:3.11-slim

  WORKDIR /app

  # 複製並安裝依賴
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # 複製應用程式碼
  COPY . .

  # Cloud Run 使用 PORT 環境變數
  EXPOSE 8080

  # 啟動應用
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
  ```

- [x] `backend/.dockerignore`
  ```
  # Python
  __pycache__/
  *.py[cod]
  *$py.class
  *.so
  .Python
  venv/
  .venv/
  ENV/
  env/

  # IDE
  .vscode/
  .idea/
  *.swp
  *.swo

  # Environment
  .env
  .env.local
  .env.*.local

  # Data (本地開發用)
  data/
  *.db

  # Credentials (不應打包進容器)
  credentials/
  *.json

  # Git
  .git/
  .gitignore

  # Testing
  .pytest_cache/
  .coverage
  htmlcov/

  # Logs
  *.log

  # Misc
  .DS_Store
  Thumbs.db
  ```

- [x] 設定 Secret Manager
  ```bash
  # 設定專案
  gcloud config set project ai-accounting-482914

  # 建立 secrets
  echo -n "your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
  echo -n "your-jwt-secret" | gcloud secrets create JWT_SECRET_KEY --data-file=-
  echo -n "your-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
  echo -n "your-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-
  echo -n "libsql://ai-accounting-waynezprog.aws-ap-northeast-1.turso.io" | gcloud secrets create TURSO_DATABASE_URL --data-file=-
  echo -n "your-turso-token" | gcloud secrets create TURSO_AUTH_TOKEN --data-file=-
  ```

- [x] 授予 Secret Manager 存取權限
  ```bash
  # 取得 Compute Engine 服務帳號
  PROJECT_NUMBER=$(gcloud projects describe ai-accounting-482914 --format='value(projectNumber)')

  # 授予權限
  gcloud projects add-iam-policy-binding ai-accounting-482914 \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
  ```

- [x] 部署至 Cloud Run
  ```bash
  cd backend

  # 建構映像
  docker build -t gcr.io/ai-accounting-482914/ai-accounting-api .

  # 推送映像
  docker push gcr.io/ai-accounting-482914/ai-accounting-api

  # 部署
  gcloud run deploy ai-accounting-api \
      --image gcr.io/ai-accounting-482914/ai-accounting-api \
      --platform managed \
      --region asia-east1 \
      --allow-unauthenticated \
      --port 8080 \
      --memory 512Mi \
      --cpu 1 \
      --min-instances 0 \
      --max-instances 10 \
      --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest,\
  JWT_SECRET_KEY=JWT_SECRET_KEY:latest,\
  GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest,\
  GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest,\
  TURSO_DATABASE_URL=TURSO_DATABASE_URL:latest,\
  TURSO_AUTH_TOKEN=TURSO_AUTH_TOKEN:latest" \
      --set-env-vars "ENV=production,\
  GOOGLE_REDIRECT_URI=https://ai-accounting-api-51386650140.asia-east1.run.app/api/auth/google/callback,\
  FRONTEND_URL=https://frontend-omega-eight-30.vercel.app,\
  CORS_ORIGINS=https://frontend-omega-eight-30.vercel.app"
  ```

- [x] Cloud Run URL
  - `https://ai-accounting-api-51386650140.asia-east1.run.app`

### 6.4 Vercel 前端部署 ✅

- [x] 安裝 Vercel CLI
  ```bash
  npm install -g vercel
  ```

- [x] 登入 Vercel
  ```bash
  vercel login
  ```

- [x] 建立 `frontend/vercel.json`
  ```json
  {
    "$schema": "https://openapi.vercel.sh/vercel.json",
    "framework": "vite",
    "buildCommand": "npm run build",
    "outputDirectory": "dist",
    "installCommand": "npm install",
    "rewrites": [
      {
        "source": "/(.*)",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "/(.*)",
        "headers": [
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          },
          {
            "key": "X-Frame-Options",
            "value": "DENY"
          },
          {
            "key": "X-XSS-Protection",
            "value": "1; mode=block"
          }
        ]
      }
    ]
  }
  ```

- [x] 設定環境變數
  ```bash
  vercel env add VITE_API_BASE_URL production <<< "https://ai-accounting-api-51386650140.asia-east1.run.app"
  ```

- [x] 部署前端
  ```bash
  cd frontend
  vercel --prod
  ```

- [x] Vercel URL
  - `https://frontend-omega-eight-30.vercel.app`

### 6.5 更新 OAuth 設定 ⚠️ 需手動完成

- [ ] 更新 GCP OAuth 重新導向 URI
  1. 前往 [GCP Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials?project=ai-accounting-482914)
  2. 編輯 OAuth 2.0 Client ID
  3. 在「已授權的重新導向 URI」新增：
     - `https://ai-accounting-api-51386650140.asia-east1.run.app/api/auth/google/callback`
  4. 在「已授權的 JavaScript 來源」新增：
     - `https://frontend-omega-eight-30.vercel.app`
  5. 儲存

- [ ] 新增測試使用者（如果應用程式在測試模式）
  1. 前往 [OAuth 同意畫面](https://console.cloud.google.com/apis/credentials/consent?project=ai-accounting-482914)
  2. 滾動到「測試使用者」區塊
  3. 點擊「+ ADD USERS」
  4. 加入你的 Google 帳號
  5. 儲存

### 6.6 CORS 設定 ✅

- [x] 後端 CORS 設定已包含 Vercel 域名
  ```bash
  CORS_ORIGINS=https://frontend-omega-eight-30.vercel.app,http://localhost:5173
  ```

### 6.7 驗證部署 ✅

- [x] 測試健康檢查
  ```bash
  curl https://ai-accounting-api-51386650140.asia-east1.run.app/health
  # {"status":"healthy","service":"ai-accounting"}
  ```

- [x] 測試前端頁面載入
  ```bash
  curl -I https://frontend-omega-eight-30.vercel.app
  # HTTP/2 200
  ```

- [ ] 測試 Google OAuth 登入流程（需先完成 6.5）

- [ ] 測試記帳功能（需先完成 OAuth）

- [ ] 測試 Siri 捷徑（更新 API URL）

---

## 環境設定檔

### 開發/生產環境分離

已建立以下環境設定檔：

| 檔案 | 用途 |
|------|------|
| `backend/.env.development` | 後端開發環境（本地 SQLite） |
| `backend/.env.production` | 後端生產環境參考（實際值在 Secret Manager） |
| `frontend/.env.development` | 前端開發環境（localhost:8000） |
| `frontend/.env.production` | 前端生產環境（Cloud Run URL） |

### 後端環境變數 (Cloud Run)

| 變數 | 說明 | 來源 |
|------|------|------|
| `OPENAI_API_KEY` | OpenAI API 金鑰 | Secret Manager |
| `GOOGLE_CLIENT_ID` | OAuth Client ID | Secret Manager |
| `GOOGLE_CLIENT_SECRET` | OAuth Client Secret | Secret Manager |
| `TURSO_DATABASE_URL` | Turso 資料庫 URL | Secret Manager |
| `TURSO_AUTH_TOKEN` | Turso 認證 Token | Secret Manager |
| `JWT_SECRET_KEY` | JWT 簽署密鑰 | Secret Manager |
| `GOOGLE_REDIRECT_URI` | OAuth 回調 URL | 環境變數 |
| `FRONTEND_URL` | 前端 URL | 環境變數 |
| `CORS_ORIGINS` | 允許的來源 | 環境變數 |
| `ENV` | 環境 (production) | 環境變數 |

### 前端環境變數 (Vercel)

| 變數 | 說明 | 值 |
|------|------|-----|
| `VITE_API_BASE_URL` | 後端 API URL | `https://ai-accounting-api-51386650140.asia-east1.run.app` |

---

## 部署腳本

已建立以下部署腳本（位於 `scripts/` 目錄）：

### `scripts/deploy-backend.sh`

一鍵部署後端至 Cloud Run：

```bash
./scripts/deploy-backend.sh
```

功能：
1. 設定 GCP 專案
2. 建構 Docker 映像
3. 推送至 Container Registry
4. 部署至 Cloud Run（含 Secrets 和環境變數）
5. 執行健康檢查

### `scripts/deploy-frontend.sh`

一鍵部署前端至 Vercel：

```bash
./scripts/deploy-frontend.sh
```

功能：
1. 安裝依賴
2. 建構生產版本
3. 部署至 Vercel

### `start.sh`（根目錄）

整合啟動腳本，支援開發/生產模式：

```bash
# 開發模式（預設）
./start.sh
./start.sh dev

# 生產模式（本地測試生產設定）
./start.sh prod
```

| 項目 | 開發模式 (dev) | 生產模式 (prod) |
|-----|---------------|----------------|
| 後端環境檔 | `.env.development` | `.env.production` |
| 前端環境檔 | `.env.development` | `.env.production` |
| 後端啟動 | `--reload`（熱重載）| 無 `--reload` |
| 前端啟動 | `npm run dev` | `npm run build && npm run preview` |
| 前端 Port | 5173 | 4173 |

功能：
1. 自動複製對應環境設定檔
2. 檢查並安裝依賴
3. 啟動後端（uvicorn）
4. 啟動前端（vite/preview）
5. 支援 Ctrl+C 同時停止所有服務

### `scripts/dev.sh`（備用）

功能已整合至根目錄 `start.sh`。

---

## 故障排除

### 資料庫連線失敗

```bash
# 使用 Turso CLI 檢查連線
turso db shell ai-accounting

# 檢查資料庫狀態
turso db show ai-accounting
```

### Cloud Run 部署失敗

```bash
# 查看部署日誌
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ai-accounting-api" --limit 50

# 查看最新版本狀態
gcloud run services describe ai-accounting-api --region asia-east1
```

### Container 啟動失敗

常見問題：
1. **libsql dialect not found**：確認使用 `sqlalchemy-libsql==0.2.0`，不是 `libsql-sqlalchemy`
2. **Secret Manager 權限不足**：確認已授予 `secretmanager.secretAccessor` 角色
3. **PORT 環境變數衝突**：Cloud Run 自動設定 PORT，不要在 `--set-env-vars` 中指定

### OAuth 回調失敗

- 確認 `GOOGLE_REDIRECT_URI` 與 GCP Console 設定一致
- 確認已加入 Vercel 域名到授權 JavaScript 來源
- 如果應用程式在測試模式，確認已加入測試使用者

### CORS 錯誤

```bash
# 更新 CORS 設定（注意使用 ^@^ 分隔符處理逗號）
gcloud run services update ai-accounting-api \
    --region asia-east1 \
    --set-env-vars "^@^CORS_ORIGINS=https://frontend-omega-eight-30.vercel.app,http://localhost:5173@ENV=production"
```

---

## Turso vs 其他資料庫比較

| 項目 | Turso | Supabase | PlanetScale |
|------|-------|----------|-------------|
| 資料庫類型 | SQLite (libSQL) | PostgreSQL | MySQL |
| 延遲 | 極低（邊緣節點） | 低（新加坡節點） | 低 |
| 免費額度 | 9GB 儲存、500M 讀取 | 500MB 儲存 | 1GB 儲存 |
| 程式碼改動 | 較小（SQLite 相容） | 需改 driver | 需改 driver |
| SQLAlchemy 支援 | `sqlalchemy-libsql` | `asyncpg` | `pymysql` |
| 適合場景 | 讀取密集、全球分布 | 完整 PostgreSQL 功能 | MySQL 生態系 |

---

## 部署檢查清單

- [x] Turso 資料庫可連線
- [x] Cloud Run 服務正常運行
- [x] Vercel 前端可存取
- [x] 環境變數已設定
- [x] CORS 設定正確
- [x] OAuth 重定向 URI 已更新
- [ ] Google OAuth 驗證審核中（需提供範圍說明和示範影片）
- [ ] OAuth 登入流程正常（驗證通過後）
- [ ] 記帳功能正常（驗證通過後）
- [ ] TTS 語音播放正常
- [ ] Siri 捷徑可連接（更新 URL 後）

---

## CI/CD（可選）

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - uses: google-github-actions/setup-gcloud@v2
      - run: |
          cd backend
          gcloud run deploy ai-accounting-api \
            --source . \
            --region asia-east1

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

---

## 下一步

1. **完成 Google OAuth 驗證**：
   - 填寫範圍說明（說明為何需要 drive.file 和 spreadsheets 權限）
   - 上傳示範影片（展示 OAuth 登入和記帳流程）
   - 等待 Google 審核通過
2. **測試完整流程**：登入 → 建立 Sheet → 記帳 → 查詢
3. **更新 Siri 捷徑**：將 API URL 更新為生產環境
4. **監控與日誌**：設定 Cloud Logging 警報

---

## 專案完成！

語音記帳助手已成功部署至雲端。

### 生產環境 URL

- **前端**：https://frontend-omega-eight-30.vercel.app
- **後端 API**：https://ai-accounting-api-51386650140.asia-east1.run.app
- **API 文件**：https://ai-accounting-api-51386650140.asia-east1.run.app/docs

### 後續可擴充功能

- [ ] 預算設定與提醒
- [ ] 記帳歷史查詢與篩選
- [ ] 資料匯出（CSV/Excel）
- [ ] 多幣別支援
- [ ] 週期性支出追蹤
- [ ] 分享帳本功能
- [ ] React Native App（Phase 7）
