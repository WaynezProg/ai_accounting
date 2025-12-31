# Phase 0：重構專案結構 ✅ 已完成

## 目標

參考現有 `note_money/` 功能，建立符合 task.md 規劃的新專案結構。

---

## 前置條件 ✅

- [x] GCP 專案設定（使用既有 Service Account）
- [x] Service Account 憑證已下載
- [x] Google Sheets API 已啟用

---

## 完成項目

### 0.1 後端專案初始化 ✅

- [x] 建立 `backend/` 目錄結構
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py              # FastAPI 入口
  │   ├── config.py            # 環境變數設定
  │   ├── api/
  │   │   ├── __init__.py
  │   │   ├── accounting.py    # 記帳 API 端點
  │   │   ├── auth.py          # 認證 API 端點
  │   │   └── health.py        # 健康檢查
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── google_sheets.py # Google Sheets 操作
  │   │   └── openai_service.py # LLM 解析
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── schemas.py       # Pydantic 模型
  │   │   └── token.py         # Token 管理
  │   └── utils/
  │       ├── __init__.py
  │       ├── auth.py          # 認證工具
  │       ├── categories.py    # 預設類別定義
  │       └── exceptions.py    # 自訂例外
  ├── data/                    # Token 儲存
  ├── credentials/             # Service Account 憑證
  ├── requirements.txt
  ├── .env.example
  └── .env
  ```
- [x] 建立 Python 虛擬環境
- [x] 建立 `requirements.txt`
  - fastapi, uvicorn
  - openai
  - pygsheets, pandas
  - google-api-python-client, google-auth
  - python-dotenv
  - pydantic, pydantic-settings
- [x] 建立 `.env.example` 範本

### 0.2 環境變數設定 ✅

- [x] 建立 `backend/.env`
  ```bash
  # OpenAI
  OPENAI_API_KEY=sk-xxx
  OPENAI_MODEL=gpt-4-turbo

  # Google Sheets (Service Account)
  GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
  GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/xxx
  GOOGLE_SHEET_WORKSHEET=記帳

  # Server
  HOST=0.0.0.0
  PORT=8000
  ENV=development

  # CORS
  CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
  ```

### 0.3 遷移現有功能 ✅

| 原檔案 | 新位置 | 狀態 |
|--------|--------|:----:|
| `note_money/main.py` | `backend/app/main.py` | ✅ |
| LLM 邏輯 | `backend/app/services/openai_service.py` | ✅ |
| Sheets 邏輯 | `backend/app/services/google_sheets.py` | ✅ |
| API 路由 | `backend/app/api/accounting.py` | ✅ |

### 0.4 驗證功能 ✅

- [x] 後端可啟動 (`uvicorn app.main:app --reload`)
- [x] `GET /health` 回應正常
- [x] `POST /api/accounting/record` 可接收請求
- [x] LLM 解析功能正常
- [x] Google Sheets 寫入成功

---

## 完成條件 ✅

- [x] 新結構可執行且功能與 `note_money/` 一致
- [x] API 端點改為 `/api/accounting/record`
- [x] 程式碼結構符合 task.md 規劃
- [x] 環境變數正確設定

---

## 下一階段

→ [Phase 1：後端核心功能](./phase-1-backend-core.md) ✅ 已完成
