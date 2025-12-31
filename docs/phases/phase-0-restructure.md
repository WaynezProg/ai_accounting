# Phase 0：重構專案結構

## 目標

參考現有 `note_money/` 功能，建立符合 task.md 規劃的新專案結構。

---

## 前置條件

- [ ] 新 GCP 專案已建立
- [ ] Service Account 憑證已下載
- [ ] Google Sheets API 已啟用

---

## 任務清單

### 0.1 後端專案初始化

- [ ] 建立 `backend/` 目錄結構
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py              # FastAPI 入口
  │   ├── config.py            # 環境變數設定
  │   ├── api/
  │   │   ├── __init__.py
  │   │   ├── accounting.py    # 記帳 API 端點
  │   │   └── health.py        # 健康檢查
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── google_sheets.py # Google Sheets 操作
  │   │   └── openai_service.py # LLM 解析
  │   ├── models/
  │   │   ├── __init__.py
  │   │   └── schemas.py       # Pydantic 模型
  │   └── utils/
  │       ├── __init__.py
  │       └── categories.py    # 預設類別定義
  ├── requirements.txt
  ├── .env.example
  └── .env
  ```
- [ ] 建立 Python 虛擬環境
- [ ] 建立 `requirements.txt`
  - fastapi
  - uvicorn
  - openai
  - pygsheets
  - google-api-python-client
  - google-auth
  - python-dotenv
  - pydantic
- [ ] 建立 `.env.example` 範本

### 0.2 環境變數設定

- [ ] 建立 `backend/.env`
  ```bash
  # OpenAI
  OPENAI_API_KEY=sk-xxx

  # Google Sheets (Service Account)
  GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
  GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/xxx

  # Server
  HOST=0.0.0.0
  PORT=8000
  ENV=development
  ```

### 0.3 遷移現有功能

參考 `note_money/` 的實作：

| 原檔案 | 新位置 | 說明 |
|--------|--------|------|
| `note_money/main.py` | `backend/app/main.py` | FastAPI 入口 |
| `note_money/note_money/note_handler.py` | 拆分至 services/ | 分離關注點 |
| - LLM 邏輯 | `backend/app/services/openai_service.py` | OpenAI 呼叫 |
| - Sheets 邏輯 | `backend/app/services/google_sheets.py` | Google Sheets 操作 |
| - API 路由 | `backend/app/api/accounting.py` | 記帳端點 |

### 0.4 驗證功能

- [ ] 後端可啟動 (`uvicorn app.main:app --reload`)
- [ ] `GET /health` 回應正常
- [ ] `POST /api/accounting/record` 可接收請求
- [ ] LLM 解析功能正常
- [ ] Google Sheets 寫入成功

---

## 完成條件

- [ ] 新結構可執行且功能與 `note_money/` 一致
- [ ] API 端點改為 `/api/accounting/record`
- [ ] 程式碼結構符合 task.md 規劃
- [ ] 環境變數正確設定

---

## 下一階段

完成後進入 [Phase 1：後端核心功能](./phase-1-backend-core.md)
