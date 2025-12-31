# 語音記帳助手

整合 Siri 捷徑、LLM 和 Google Sheets 的智慧記帳系統。

## 功能特色

- 🎙️ **語音記帳**：透過 Siri 捷徑或網頁語音輸入記帳
- 🤖 **AI 智慧解析**：使用 GPT-4 自動解析記帳內容（日期、金額、類別）
- 📊 **Google Sheets 儲存**：記帳資料自動寫入 Google Sheets
- 💡 **理財回饋**：每次記帳後提供 AI 理財建議
- 🔐 **多重認證**：Google OAuth 登入 + API Token 認證
- 🗣️ **自然語音**：OpenAI TTS 自然語音回饋（可選）
- 📈 **統計圖表**：圓餅圖視覺化支出分佈
- 🔍 **智慧查詢**：自然語言查詢帳務狀況
- 👤 **個人專屬 Sheet**：每個用戶擁有獨立的 Google Sheet

---

## 開發進度

### ✅ 已完成

| Phase | 功能 | 說明 |
|-------|------|------|
| 0 | 專案結構 | FastAPI 後端架構、環境設定 |
| 1 | 後端核心 | 記帳 API、LLM 解析、Google Sheets、統計查詢、理財回饋 |
| 2 | Siri 整合 | API Token 認證、Siri 捷徑設定文件 |
| 3 | 前端基礎 | React + shadcn/ui 網頁介面、語音輸入/輸出 |
| 4 | 功能整合 | 統計圖表、查詢介面、Token 管理、自然語音 |
| 5 | Google OAuth | 用戶登入、個人專屬 Sheet、JWT 認證 |

### 🔲 待開發

| Phase | 功能 | 說明 |
|-------|------|------|
| 6 | 部署 | GCP 部署、CI/CD |

---

## 快速開始

### 前置需求

- Python 3.11+
- Node.js 18+
- OpenAI API Key
- Google Cloud 專案 + Service Account
- Google OAuth 2.0 憑證（可選，用於用戶登入）

### 一鍵啟動

```bash
# 同時啟動前後端
./start.sh
```

- 前端：http://localhost:5173
- 後端 API：http://localhost:8000
- API 文件：http://localhost:8000/docs

### 手動安裝

**後端：**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**前端：**
```bash
cd frontend
npm install
```

### 設定環境變數

```bash
# 複製範本
cp backend/.env.example backend/.env

# 編輯 .env 填入你的設定
```

**.env 必填項目：**

```bash
# 基本設定
OPENAI_API_KEY=sk-xxx
GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/xxx

# Google OAuth（可選，用於用戶登入）
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx

# JWT（用於 OAuth 登入）
JWT_SECRET_KEY=your-secret-key
```

### 分別啟動

**後端：**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**前端：**
```bash
cd frontend
npm run dev
```

---

## 技術棧

### 後端
- **框架**：FastAPI (Python 3.11+)
- **LLM**：OpenAI GPT-4 Turbo
- **TTS**：OpenAI TTS API
- **資料儲存**：Google Sheets (Service Account / OAuth)
- **資料庫**：SQLite + SQLAlchemy (async)
- **認證**：JWT + API Token

### 前端
- **框架**：React + TypeScript + Vite
- **UI**：shadcn/ui (Radix UI + Tailwind CSS v4)
- **路由**：react-router-dom
- **圖表**：recharts
- **語音 STT**：Web Speech API（免費）
- **語音 TTS**：OpenAI TTS（付費，可選）+ Web Speech API（免費）
- **HTTP**：Axios

---

## 前端頁面

| 路徑 | 頁面 | 功能 |
|------|------|------|
| `/` | 記帳首頁 | 語音/文字記帳輸入、記帳結果顯示 |
| `/stats` | 統計頁面 | 月度支出統計、圓餅圖、類別明細 |
| `/query` | 查詢頁面 | 自然語言帳務查詢、語音回覆 |
| `/settings` | 設定頁面 | 帳戶管理、Sheet 設定、Token 管理、語音設定 |
| `/auth/callback` | OAuth 回調 | Google 登入後的回調處理 |

---

## API 端點

### 認證 API

| 方法 | 路徑 | 認證 | 說明 |
|------|------|:----:|------|
| GET | `/api/auth/google/login` | ❌ | 導向 Google OAuth 登入 |
| GET | `/api/auth/google/callback` | ❌ | OAuth 回調處理 |
| POST | `/api/auth/logout` | ✅ | 登出 |
| GET | `/api/auth/me` | ✅ | 取得當前用戶資訊 |
| GET | `/api/auth/status` | ❌ | 檢查認證狀態 |
| POST | `/api/auth/token/generate` | ❌ | 產生 API Token |
| GET | `/api/auth/token/list` | ✅ | 列出用戶的 API Token |
| DELETE | `/api/auth/token/{id}` | ✅ | 撤銷 API Token |
| GET | `/api/auth/token/verify` | ✅ | 驗證 Token |

### Sheet API

| 方法 | 路徑 | 認證 | 說明 |
|------|------|:----:|------|
| GET | `/api/sheets/my-sheet` | ✅ | 取得用戶的 Sheet 資訊 |
| POST | `/api/sheets/create` | ✅ | 建立新的 Sheet |
| POST | `/api/sheets/link` | ✅ | 連結現有的 Sheet |

### 記帳 API

| 方法 | 路徑 | 認證 | 說明 |
|------|------|:----:|------|
| POST | `/api/accounting/record` | ✅ | 記帳 |
| GET | `/api/accounting/stats` | ✅ | 月度統計 |
| POST | `/api/accounting/query` | ✅ | 自然語言查詢 |
| GET | `/api/accounting/categories` | ❌ | 類別清單 |

### 其他 API

| 方法 | 路徑 | 認證 | 說明 |
|------|------|:----:|------|
| GET | `/health` | ❌ | 健康檢查 |
| POST | `/api/speech/synthesize` | ✅ | 文字轉語音 (TTS) |
| GET | `/api/speech/voices` | ❌ | 可用語音列表 |

> **認證說明：**
> - ✅ 需要在 Header 提供 `Authorization: Bearer <token>`（JWT 或 API Token）
> - ❌ 不需要認證

---

## 使用流程

### 網頁版

1. 開啟網頁 http://localhost:5173
2. 點擊「使用 Google 帳號登入」
3. 授權應用程式存取 Google Sheets
4. 在設定頁面建立專屬的 Google Sheet
5. 開始記帳！

### Siri 捷徑

1. 在網頁設定頁面登入後，產生 API Token
2. 在 iPhone「捷徑」App 建立新捷徑
3. 加入「聽寫文字」→「取得 URL 內容」→「朗讀文字」
4. 設定語音觸發：「嘿 Siri，記一筆帳」

詳細設定步驟請參考 [Siri 捷徑設定教學](docs/siri-shortcut-setup.md)。

---

## 專案結構

```
ai_accounting/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 環境設定
│   │   ├── api/
│   │   │   ├── health.py        # 健康檢查
│   │   │   ├── auth.py          # 認證 API（OAuth + Token）
│   │   │   ├── accounting.py    # 記帳 API
│   │   │   ├── sheets.py        # Sheet 管理 API
│   │   │   └── speech.py        # TTS API
│   │   ├── database/
│   │   │   ├── engine.py        # SQLAlchemy 設定
│   │   │   ├── models.py        # 資料庫模型
│   │   │   └── crud.py          # CRUD 操作
│   │   ├── services/
│   │   │   ├── openai_service.py
│   │   │   ├── google_sheets.py
│   │   │   ├── user_sheets_service.py
│   │   │   ├── oauth_service.py
│   │   │   └── jwt_service.py
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic 模型
│   │   └── utils/
│   │       ├── auth.py          # 認證工具
│   │       ├── categories.py    # 類別定義
│   │       └── exceptions.py    # 自訂例外
│   ├── credentials/             # Service Account 憑證
│   ├── data/                    # SQLite 資料庫
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # 路由設定
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx  # 認證狀態管理
│   │   ├── pages/
│   │   │   ├── HomePage.tsx     # 記帳首頁
│   │   │   ├── StatsPage.tsx    # 統計頁面
│   │   │   ├── QueryPage.tsx    # 查詢頁面
│   │   │   ├── SettingsPage.tsx # 設定頁面
│   │   │   ├── AuthCallbackPage.tsx
│   │   │   └── AuthErrorPage.tsx
│   │   ├── components/
│   │   │   ├── layout/          # 佈局元件
│   │   │   └── ui/              # shadcn/ui 元件
│   │   ├── hooks/               # 自訂 Hooks
│   │   └── services/            # API 服務
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── phases/                  # 開發階段文件
│   └── siri-shortcut-setup.md   # Siri 設定教學
├── start.sh                     # 一鍵啟動腳本
└── README.md
```

---

## 開發文件

詳細的開發任務規劃請參考：

- [task.md](task.md) - 完整專案規劃
- [docs/phases/](docs/phases/) - 各階段開發文件
  - [Phase 0: 重構專案結構](docs/phases/phase-0-restructure.md) ✅
  - [Phase 1: 後端核心功能](docs/phases/phase-1-backend-core.md) ✅
  - [Phase 2: Siri 捷徑整合](docs/phases/phase-2-siri-integration.md) ✅
  - [Phase 3: 前端基礎建設](docs/phases/phase-3-frontend.md) ✅
  - [Phase 4: 前端功能整合](docs/phases/phase-4-enhancements.md) ✅
  - [Phase 5: Google OAuth](docs/phases/phase-5-oauth.md) ✅
  - [Phase 6: 部署與文件](docs/phases/phase-6-deployment.md) 🔲

---

## 未來規劃

- [ ] 預算設定與提醒
- [ ] 記帳歷史查詢與篩選
- [ ] 資料匯出（CSV/Excel）
- [ ] GCP 雲端部署
- [ ] PWA 支援

---

## License

MIT
