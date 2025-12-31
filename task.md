# 語音記帳助手專案任務規劃

## 專案概述

語音記帳助手是一個整合 Siri 捷徑、LLM 和 Google Sheets 的記帳系統，支援手機端和網頁端，提供自動分類記帳和理財回饋功能。

---

## 專案確認需求

| 項目 | 決定 |
|------|------|
| Google Sheets 模式 | 每個用戶自己的 Sheet（OAuth 2.0 用戶授權） |
| Siri 捷徑認證 | API Key / Token（網頁端產生，手動設定到捷徑） |
| 開發環境 | 本地開發（後端 8000、前端 5173） |
| 部署環境 | Google Cloud Platform (GCP) |
| 記帳類別 | 混合模式（預設類別 + LLM 可建議新類別） |
| Token 儲存 | SQLite（本地）/ Cloud SQL（GCP） |
| 前端 UI | shadcn/ui (Radix UI + Tailwind CSS) |

---

## 技術棧

- **後端**: FastAPI (Python)
- **前端**: React + TypeScript + Vite
- **UI 框架**: shadcn/ui (Radix UI + Tailwind CSS)
- **LLM**: OpenAI API
- **資料儲存**:
  - 記帳資料：Google Sheets API（用戶自己的 Sheet）
  - Token/用戶資料：SQLite（本地）/ Cloud SQL（GCP）
- **認證**:
  - 網頁端：Google OAuth 2.0
  - Siri 捷徑：API Token（Bearer Token）
- **語音處理**:
  - 手機端: Siri 捷徑內建語音識別
  - 網頁端 STT: Web Speech API
  - 網頁端 TTS: OpenAI TTS API (`gpt-4o-mini-tts` 模型，支援 11 種聲音)

## 系統架構

```
┌─────────────────┐        ┌───────────────────────────────────────┐
│   Siri 捷徑     │───────▶│                                       │
│ (語音→文字→API) │  Token │                                       │
└─────────────────┘        │         FastAPI 後端                   │
                           │                                       │
┌─────────────────┐        │  ┌─────────────┐  ┌───────────────┐  │
│   React 網頁    │───────▶│  │ Auth 模組   │  │ OpenAI 模組   │  │
│ (STT/TTS/OAuth) │ OAuth  │  │ (OAuth2.0)  │  │ (解析/回饋)   │  │
└─────────────────┘        │  └─────────────┘  └───────────────┘  │
                           │                                       │
                           │  ┌─────────────┐  ┌───────────────┐  │
                           │  │ SQLite      │  │ Sheets 模組   │  │
                           │  │ (Token/用戶)│  │ (記帳資料)    │  │
                           │  └─────────────┘  └───────────────┘  │
                           └───────────────────────────────────────┘
                                            │
                                            ▼
                           ┌───────────────────────────────────────┐
                           │  用戶的 Google Drive                  │
                           │  └── 記帳 Sheet (自動建立)            │
                           └───────────────────────────────────────┘
```

## 資料流程

1. **語音輸入** → STT 轉文字
2. **文字** → FastAPI 後端
3. **後端** → OpenAI LLM 處理（分類、解析）
4. **後端** → 寫入 Google Sheets
5. **後端** → 查詢統計資料
6. **後端** → LLM 生成理財回饋
7. **後端** → 返回文字/語音反饋

---

## 目錄結構

```
ai_accounting/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 環境變數設定
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # OAuth 2.0 端點
│   │   │   ├── accounting.py    # 記帳 API 端點
│   │   │   └── health.py        # 健康檢查
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── google_sheets.py # Google Sheets 操作
│   │   │   ├── openai_service.py # LLM 解析與回饋
│   │   │   ├── token_service.py  # Token 管理
│   │   │   └── database.py       # SQLite 資料庫
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py       # Pydantic 模型
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── categories.py    # 預設類別定義
│   ├── tests/
│   │   └── ...
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/              # shadcn/ui 元件
│   │   │   ├── VoiceRecorder.tsx
│   │   │   ├── VoicePlayer.tsx
│   │   │   └── AccountingResult.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── hooks/
│   │   │   ├── useSpeechRecognition.ts
│   │   │   └── useSpeechSynthesis.ts
│   │   ├── lib/
│   │   │   └── utils.ts         # shadcn/ui cn() helper
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── components.json          # shadcn/ui 設定
│   ├── package.json
│   ├── tailwind.config.js
│   ├── .env.example
│   └── vite.config.ts
├── deploy/
│   ├── gcp/
│   │   ├── cloudbuild.yaml      # Cloud Build CI/CD
│   │   ├── app-backend.yaml     # App Engine 後端設定
│   │   ├── app-frontend.yaml    # App Engine 前端設定
│   │   └── Dockerfile           # Cloud Run 用
│   └── docker-compose.yml       # 本地 Docker 開發
├── docs/
│   └── siri-shortcut-setup.md   # Siri 捷徑設定教學
└── README.md
```

---

## 環境變數

### 後端 (.env)
```bash
# OpenAI
OPENAI_API_KEY=sk-xxx

# Google OAuth 2.0
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# 安全
SECRET_KEY=random-secret-for-token-signing

# 資料庫
# 本地開發用 SQLite
DATABASE_URL=sqlite:///./data.db
# GCP 生產環境用 Cloud SQL（PostgreSQL）
# DATABASE_URL=postgresql://user:pass@/dbname?host=/cloudsql/project:region:instance

# 環境
ENV=development  # development | production
```

### 前端 (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## API 端點總覽

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/auth/google/login` | 開始 OAuth 流程 | - |
| GET | `/api/auth/google/callback` | OAuth 回調 | - |
| POST | `/api/auth/token/generate` | 產生 API Token（給 Siri 用） | OAuth |
| GET | `/api/auth/status` | 檢查認證狀態 | OAuth/Token |
| POST | `/api/auth/logout` | 登出 | OAuth |
| POST | `/api/accounting/record` | 記帳 | OAuth/Token |
| GET | `/api/accounting/stats` | 統計資料 | OAuth/Token |
| POST | `/api/accounting/query` | 帳務查詢 | OAuth/Token |
| GET | `/api/accounting/categories` | 類別清單 | OAuth/Token |
| POST | `/api/speech/synthesize` | 文字轉語音 (TTS) | OAuth/Token |
| GET | `/api/speech/voices` | 取得可用聲音列表 | - |
| GET | `/api/sheets/list` | 列出 Google Drive 中的 Sheets | OAuth |
| POST | `/api/sheets/select` | 選擇現有 Sheet | OAuth |
| POST | `/api/sheets/create` | 建立新 Sheet | OAuth |
| GET | `/api/sheets/my-sheet` | 取得用戶的 Sheet 資訊 | OAuth |
| GET | `/api/auth/me` | 取得當前用戶資訊 | OAuth |
| GET | `/api/auth/token/list` | 列出用戶的 API Tokens | OAuth |
| DELETE | `/api/auth/token/{id}` | 撤銷 API Token | OAuth |
| GET | `/health` | 健康檢查 | - |

---

## 任務清單

### 階段一：專案初始化與環境設定

#### 1.1 後端專案初始化
- [ ] 建立 FastAPI 專案結構
- [ ] 設定 Python 虛擬環境
- [ ] 建立 `requirements.txt`（FastAPI, uvicorn, openai, google-api-python-client, google-auth 等）
- [ ] 設定環境變數管理（`.env` 檔案）
- [ ] 建立專案目錄結構：
  ```
  backend/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── api/
    │   ├── services/
    │   ├── models/
    │   └── utils/
    ├── requirements.txt
    └── .env.example
  ```

#### 1.2 前端專案初始化
- [ ] 建立 React 專案（使用 Vite 或 Create React App）
- [ ] 設定專案結構：
  ```
  frontend/
    ├── src/
    │   ├── components/
    │   ├── services/
    │   ├── hooks/
    │   └── utils/
    ├── package.json
    └── .env.example
  ```
- [ ] 安裝必要套件（axios, react-speech-kit 或 Web Speech API）

#### 1.3 Google Cloud 專案設定
- [ ] 建立 Google Cloud 專案
- [ ] 啟用 Google Sheets API
- [ ] 建立 OAuth 2.0 憑證（Web Application）
- [ ] 設定授權重新導向 URI
- [ ] 下載憑證 JSON 檔案

#### 1.4 OpenAI API 設定
- [ ] 取得 OpenAI API Key
- [ ] 設定環境變數

---

### 階段二：後端核心功能開發

#### 2.1 FastAPI 基礎架構
- [ ] 建立 FastAPI 應用程式主檔
- [ ] 設定 CORS 中間件
- [ ] 建立 API 路由結構
- [ ] 設定錯誤處理機制
- [ ] 建立日誌系統

#### 2.2 Google Sheets 整合服務
- [ ] 實作 Google OAuth 2.0 認證流程
- [ ] 建立 Google Sheets 服務類別
- [ ] 實作建立/讀取 Google Sheet 功能
- [ ] 實作寫入記帳資料功能
- [ ] 實作讀取統計資料功能
- [ ] 處理認證 token 刷新機制

#### 2.3 OpenAI LLM 整合服務
- [ ] 建立 OpenAI 服務類別
- [ ] 實作語音文字解析功能（提取：日期、金額、類別、備註）
- [ ] 設計 prompt 模板：
  - 記帳解析 prompt
  - 理財分析 prompt
  - 帳務查詢 prompt
- [ ] 實作錯誤處理與重試機制

#### 2.4 記帳處理邏輯
- [ ] 建立記帳資料模型（Pydantic）
- [ ] 實作記帳解析函數（LLM → 結構化資料）
- [ ] 實作資料驗證與清理
- [ ] 實作記帳寫入邏輯
- [ ] 實作統計資料查詢（當月總額、類別統計等）

#### 2.5 理財回饋邏輯
- [ ] 實作統計資料彙整功能
- [ ] 設計理財分析 prompt（包含統計資料）
- [ ] 實作理財建議生成功能
- [ ] 實作消費建議判斷邏輯

---

### 階段三：API 端點開發

#### 3.1 認證相關 API
- [ ] `POST /api/auth/google/login` - 取得 Google OAuth URL
- [ ] `GET /api/auth/google/callback` - OAuth 回調處理
- [ ] `POST /api/auth/logout` - 登出
- [ ] `GET /api/auth/status` - 檢查認證狀態

#### 3.2 記帳相關 API
- [ ] `POST /api/accounting/record` - 記錄記帳（接收語音文字）
  - 輸入: `{ "text": "中午吃排骨便當120元" }`
  - 處理: LLM 解析 → 寫入 Google Sheets → 查詢統計 → 生成回饋
  - 輸出: `{ "message": "已記錄：午餐 120元", "feedback": "理財回饋..." }`
- [ ] `GET /api/accounting/stats` - 取得統計資料
- [ ] `GET /api/accounting/query` - 查詢帳務狀況
  - 輸入: `{ "query": "這個月花了多少錢？" }`
  - 輸出: `{ "response": "理財回饋..." }`

#### 3.3 健康檢查 API
- [ ] `GET /health` - 健康檢查
- [ ] `GET /api/status` - API 狀態

---

### 階段四：前端開發

#### 4.1 基礎 UI 架構
- [ ] 建立主要頁面元件
- [ ] 設定路由（React Router）
- [ ] 建立認證狀態管理（Context 或 Redux）
- [ ] 建立 API 服務層（axios 封裝）

#### 4.2 Google OAuth 整合
- [ ] 實作 Google 登入按鈕
- [ ] 處理 OAuth 回調
- [ ] 管理認證 token（localStorage/sessionStorage）
- [ ] 實作登出功能

#### 4.3 語音輸入功能（STT）
- [ ] 整合 Web Speech API 或 react-speech-kit
- [ ] 實作語音錄製 UI
- [ ] 實作語音轉文字功能
- [ ] 處理語音識別錯誤
- [ ] 實作錄音狀態指示器

#### 4.4 語音輸出功能（TTS）
- [ ] 整合 Web Speech API TTS
- [ ] 實作文字轉語音播放
- [ ] 實作語音播放控制（播放/暫停/停止）
- [ ] 處理瀏覽器相容性

#### 4.5 記帳介面
- [ ] 建立記帳輸入頁面
- [ ] 實作語音輸入觸發按鈕
- [ ] 顯示語音識別結果
- [ ] 實作記帳提交功能
- [ ] 顯示記帳結果與回饋

#### 4.6 帳務查詢介面
- [ ] 建立查詢頁面
- [ ] 實作語音查詢功能
- [ ] 顯示查詢結果
- [ ] 實作統計圖表（可選，使用 Chart.js 或 Recharts）

#### 4.7 UI/UX 優化
- [ ] 設計響應式佈局
- [ ] 實作載入狀態
- [ ] 實作錯誤提示
- [ ] 優化語音互動體驗

---

### 階段五：Siri 捷徑整合

#### 5.1 Siri 捷徑設計
- [ ] 設計捷徑流程：
  1. 接收語音輸入
  2. 呼叫 FastAPI `/api/accounting/record` 端點
  3. 顯示/語音播放回饋結果
- [ ] 建立捷徑腳本
- [ ] 設定 API 端點 URL
- [ ] 處理認證（Bearer Token 或 API Key）
- [ ] 測試語音輸入與回饋

#### 5.2 文件撰寫
- [ ] 撰寫 Siri 捷徑設定教學
- [ ] 提供捷徑下載連結或匯入方式

---

### 階段六：Google Sheets 資料結構設計

#### 6.1 Sheet 結構設計
- [ ] 設計記帳資料表結構：
  | 日期 | 時間 | 金額 | 類別 | 備註 | 建立時間 |
  |------|------|------|------|------|----------|
- [ ] 設計統計資料表（可選，或由 API 即時計算）
- [ ] 建立預設 Sheet 範本
- [ ] 實作 Sheet 初始化功能

#### 6.2 資料處理邏輯
- [ ] 實作日期格式化
- [ ] 實作類別標準化（LLM 判斷後對應到標準類別）
- [ ] 實作資料驗證規則

---

### 階段七：測試與優化

#### 7.1 單元測試
- [ ] 後端服務單元測試
- [ ] API 端點測試
- [ ] 前端元件測試（可選）

#### 7.2 整合測試
- [ ] 完整記帳流程測試
- [ ] Google Sheets 讀寫測試
- [ ] OpenAI API 整合測試
- [ ] 語音功能測試

#### 7.3 錯誤處理優化
- [ ] API 錯誤處理完善
- [ ] 網路錯誤處理
- [ ] LLM API 失敗重試機制
- [ ] Google Sheets API 錯誤處理

#### 7.4 效能優化
- [ ] API 回應時間優化
- [ ] LLM prompt 優化（減少 token 使用）
- [ ] Google Sheets 批次寫入優化
- [ ] 前端載入效能優化

#### 7.5 安全性檢查
- [ ] API Key 安全儲存
- [ ] OAuth token 安全處理
- [ ] 輸入驗證與清理
- [ ] CORS 設定檢查

---

### 階段八：部署與文件

#### 8.1 本地部署
- [ ] 後端本地執行設定
- [ ] 前端本地執行設定
- [ ] 環境變數設定文件

#### 8.2 雲端部署（可選）
- [ ] 後端部署（Heroku/Railway/Render/AWS）
- [ ] 前端部署（Vercel/Netlify）
- [ ] 環境變數設定
- [ ] 域名設定

#### 8.3 文件撰寫
- [ ] README.md - 專案說明
- [ ] API 文件（FastAPI 自動生成或手動撰寫）
- [ ] 設定教學文件
- [ ] 使用教學文件
- [ ] Siri 捷徑設定教學

---

## API 設計規格

### POST /api/accounting/record

**請求：**
```json
{
  "text": "中午吃排骨便當120元",
  "user_id": "user_123" // 從認證 token 取得
}
```

**回應：**
```json
{
  "success": true,
  "data": {
    "record": {
      "date": "2024-01-15",
      "time": "12:30",
      "amount": 120,
      "category": "飲食",
      "note": "排骨便當"
    },
    "feedback": "已記錄午餐 120元。本月飲食類別已消費 3,500元，建議控制飲食支出。"
  }
}
```

### GET /api/accounting/stats

**請求：**
```
GET /api/accounting/stats?month=2024-01
```

**回應：**
```json
{
  "success": true,
  "data": {
    "month": "2024-01",
    "total": 15000,
    "by_category": {
      "飲食": 5000,
      "交通": 2000,
      "娛樂": 3000,
      "其他": 5000
    }
  }
}
```

### POST /api/accounting/query

**請求：**
```json
{
  "query": "這個月花了多少錢？",
  "user_id": "user_123"
}
```

**回應：**
```json
{
  "success": true,
  "data": {
    "response": "本月總支出為 15,000元。其中飲食類別佔比最高（33%），建議適度控制飲食支出。"
  }
}
```

---

## 資料模型

### 記帳記錄 (AccountingRecord)
```python
{
  "date": "2024-01-15",      # 日期
  "time": "12:30",            # 時間（可選）
  "amount": 120,             # 金額
  "category": "飲食",         # 類別
  "note": "排骨便當",         # 備註
  "created_at": "2024-01-15T12:30:00Z"  # 建立時間
}
```

---

## 現有功能參考（note_money/）

重構時參考，功能重現後刪除此資料夾。

| 項目 | 內容 |
|------|------|
| 入口 | `note_money/main.py` - FastAPI, port 8868 |
| 核心邏輯 | `note_money/note_money/note_handler.py` |
| API 端點 | `POST /note_money` - 接收 `{"data": "記帳內容"}` |
| LLM | GPT-4 Turbo，解析出：時間、名稱、類別、花費、幣別、支付方式 |
| Google Sheets | Service Account 認證，固定 Sheet URL |
| 憑證檔 | `note-money-423116-90cf1d6c33c0.json`（待替換為新 GCP 專案） |

---

## 開發進度總覽

| 階段 | 名稱 | 狀態 |
|------|------|:----:|
| Phase 0 | 重構專案結構 | ✅ 完成 |
| Phase 1 | 後端核心功能 | ✅ 完成 |
| Phase 2 | Siri 捷徑整合 | ✅ 完成 |
| Phase 3 | 前端基礎建設 | ✅ 完成 |
| Phase 4 | 前端功能整合 | ✅ 完成 |
| Phase 5 | Google OAuth 2.0 | ✅ 完成 |
| Phase 6 | 部署與文件 | 🔲 待開發 |

---

### Phase 0：重構專案結構 ✅
- 參考 `note_money/` 現有功能，建立新的 backend/ 結構
- FastAPI + OpenAI LLM 解析 + Google Sheets 寫入
- `note_money/` 已刪除

### Phase 1：後端核心功能 ✅
- 記帳 API（`POST /api/accounting/record`）
- LLM 解析（GPT-4 提取結構化資料）
- Google Sheets 寫入
- 理財回饋功能

### Phase 2：Siri 捷徑整合 ✅
- API Token 認證機制（保護 API）
- Bearer Token 驗證
- Siri 捷徑設定文件

### Phase 3：前端基礎建設 ✅
- React + TypeScript + Vite + shadcn/ui
- 語音輸入（Web Speech API STT）
- 語音輸出（Web Speech API TTS）

### Phase 4：前端功能整合 ✅
- OpenAI TTS 自然語音（`gpt-4o-mini-tts` 模型，支援 11 種聲音）
- 統計頁面（圓餅圖、類別明細）
- 查詢介面（自然語言查詢帳務）
- 設定頁面（Token 管理、語音設定）
- 底部導航列（記帳/統計/查詢/設定）

### Phase 5：Google OAuth 2.0 ✅
- Google OAuth 登入流程
- 用戶專屬 Google Sheet（使用用戶的 OAuth Token）
- SQLite 資料庫（用戶、Token、Sheet 關聯）
- JWT Session 管理
- 從 Google Drive 列出並選擇現有 Sheet（需 `drive.readonly` 權限）
- 月份分頁管理（YYYY-MM 格式，自動建立）
- API Token 綁定用戶

### Phase 6：部署與文件 🔲
- GCP 部署設定
- README 與使用文件

---

## 注意事項

1. **Google OAuth 設定**：需要設定正確的授權重新導向 URI
2. **OpenAI API 成本**：注意 token 使用量，優化 prompt
3. **Google Sheets API 限制**：注意讀寫頻率限制
4. **語音識別準確度**：Web Speech API 在不同瀏覽器表現可能不同
5. **安全性**：API Key 和 OAuth token 必須安全儲存，不可暴露在前端程式碼

---

## 後續擴充功能（可選）

- [ ] 多使用者支援
- [ ] 記帳類別自訂
- [ ] 預算設定與提醒
- [ ] 資料匯出（CSV/Excel）
- [ ] 記帳歷史查詢與篩選
- [ ] 圖表視覺化
- [ ] 多語言支援

