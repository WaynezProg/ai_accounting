# 開發階段總覽

語音記帳助手的開發任務，按階段拆分。

---

## 階段總覽

| Phase | 名稱 | 狀態 | 說明 |
|:-----:|------|:----:|------|
| 0 | [重構專案結構](./phase-0-restructure.md) | ✅ 完成 | 後端目錄結構、環境設定 |
| 1 | [後端核心功能](./phase-1-backend-core.md) | ✅ 完成 | API 端點、OpenAI、Google Sheets |
| 2 | [Siri 捷徑整合](./phase-2-siri-integration.md) | ✅ 完成 | Token 認證、Siri 設定文件 |
| 3 | [前端基礎建設](./phase-3-frontend.md) | ✅ 完成 | React + shadcn/ui + 語音 |
| 4 | [前端功能整合](./phase-4-enhancements.md) | ✅ 完成 | 自然語音、統計圖表、查詢介面 |
| 5 | [Google OAuth](./phase-5-oauth.md) | ✅ 完成 | 用戶登入、個人 Sheet、JWT 認證 |
| 6 | [部署上線](./phase-6-deployment.md) | ✅ 完成 | Cloud Run + Turso + Vercel |

---

## 生產環境

| 服務 | URL |
|------|-----|
| **前端** | https://frontend-omega-eight-30.vercel.app |
| **後端 API** | https://ai-accounting-api-51386650140.asia-east1.run.app |
| **API 文件** | https://ai-accounting-api-51386650140.asia-east1.run.app/docs |

---

## 狀態說明

- ✅ 已完成
- 🔶 進行中
- 🔲 待開發

---

## 開發順序

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
   │         │         │         │         │         │         │
   │         │         │         │         │         │         └─ 已上線 ✅
   │         │         │         │         │         └─ 多用戶支援 ✅
   │         │         │         │         └─ 前端功能完整 ✅
   │         │         │         └─ 網頁版可用 ✅
   │         │         └─ Siri 可用 ✅
   │         └─ API 可用 ✅
   └─ 專案結構就緒 ✅
```

---

## 快速里程碑

| 里程碑 | 完成 Phase | 可用功能 | 狀態 |
|--------|-----------|----------|:----:|
| MVP（最小可用） | 0, 1, 2 | Siri 語音記帳 | ✅ |
| 網頁版基礎 | + 3 | 網頁語音記帳 | ✅ |
| 網頁版完整 | + 4 | 自然語音、統計圖表、查詢介面 | ✅ |
| 多用戶 | + 5 | 用戶自己的 Sheet | ✅ |
| 生產就緒 | + 6 | 正式上線 | ✅ |

---

## 已完成功能

### Phase 0-2 完成項目

**後端核心：**
- ✅ FastAPI 應用程式架構
- ✅ OpenAI GPT-4 記帳解析（含重試機制）
- ✅ Google Sheets 讀寫（Service Account 模式）
- ✅ 理財回饋生成
- ✅ 自然語言查詢
- ✅ 月度統計功能
- ✅ 全域錯誤處理
- ✅ 日誌系統

**認證系統：**
- ✅ Bearer Token 認證
- ✅ Token 產生/驗證/撤銷
- ✅ API 端點保護

**文件：**
- ✅ Siri 捷徑設定教學
- ✅ README.md
- ✅ start.sh 啟動腳本

### Phase 3 完成項目

**前端基礎：**
- ✅ React + TypeScript + Vite 專案
- ✅ Tailwind CSS v4 + shadcn/ui
- ✅ API 服務層（axios + interceptors）
- ✅ TypeScript 完整型別定義

**語音功能：**
- ✅ Web Speech API 語音輸入 (STT)
- ✅ Web Speech API 語音輸出 (TTS) - 免費
- ✅ 繁體中文 (zh-TW) 支援
- ✅ 瀏覽器相容性檢查

### Phase 4 完成項目

**自然語音：**
- ✅ OpenAI TTS API 端點 (`/api/speech/synthesize`)
- ✅ 6 種 AI 聲音選擇（nova, shimmer, alloy, echo, fable, onyx）
- ✅ 語速調整功能
- ✅ 混合模式：STT 免費 + TTS 可選付費

**統計頁面：**
- ✅ 月份選擇器
- ✅ 總支出顯示
- ✅ 類別圓餅圖 (recharts)
- ✅ 類別明細列表

**查詢介面：**
- ✅ 自然語言查詢
- ✅ 語音輸入查詢
- ✅ 查詢範例提示
- ✅ 查詢歷史記錄

**設定頁面：**
- ✅ Token 管理（顯示、產生、複製）
- ✅ Token 驗證狀態
- ✅ 語音設定面板
- ✅ Siri 捷徑說明

**路由與導航：**
- ✅ react-router-dom 多頁面路由
- ✅ 底部導航列
- ✅ 響應式佈局

### Phase 5 完成項目

**Google OAuth：**
- ✅ Google OAuth 2.0 登入流程
- ✅ JWT Session 管理
- ✅ 用戶專屬 Google Sheet
- ✅ SQLite / Turso 資料庫
- ✅ 用戶、Token、Sheet 關聯

**Sheet 管理：**
- ✅ 建立新 Sheet
- ✅ 連結現有 Sheet
- ✅ 月份分頁管理（YYYY-MM 格式）

### Phase 6 完成項目

**部署：**
- ✅ GCP Cloud Run 後端部署
- ✅ Turso libSQL 資料庫
- ✅ Vercel 前端部署
- ✅ GCP Secret Manager 密鑰管理
- ✅ 環境分離（dev / production）
- ✅ 部署腳本（deploy-backend.sh、deploy-frontend.sh）
- ✅ 整合啟動腳本（start.sh dev/prod）

**OAuth 驗證：**
- ✅ 隱私權政策頁面
- ✅ 服務條款頁面
- ✅ Google Search Console 網站驗證
- 🔶 Google OAuth 驗證審核中

---

## API 端點總覽

| 方法 | 路徑 | 認證 | Phase | 狀態 |
|------|------|:----:|:-----:|:----:|
| GET | `/health` | ❌ | 0 | ✅ |
| POST | `/api/accounting/record` | ✅ Token | 1 | ✅ |
| GET | `/api/accounting/categories` | ❌ | 1 | ✅ |
| GET | `/api/accounting/stats` | ✅ Token | 1 | ✅ |
| POST | `/api/accounting/query` | ✅ Token | 1 | ✅ |
| POST | `/api/auth/token/generate` | ✅ OAuth | 2 | ✅ |
| GET | `/api/auth/token/verify` | ✅ Token | 2 | ✅ |
| GET | `/api/auth/token/list` | ✅ OAuth | 5 | ✅ |
| DELETE | `/api/auth/token/{id}` | ✅ OAuth | 5 | ✅ |
| GET | `/api/auth/status` | ✅ Token | 2 | ✅ |
| POST | `/api/speech/synthesize` | ✅ Token | 4 | ✅ |
| GET | `/api/speech/voices` | ❌ | 4 | ✅ |
| GET | `/api/auth/google/login` | ❌ | 5 | ✅ |
| GET | `/api/auth/google/callback` | ❌ | 5 | ✅ |
| GET | `/api/auth/me` | ✅ OAuth | 5 | ✅ |
| POST | `/api/auth/logout` | ✅ OAuth | 5 | ✅ |
| GET | `/api/sheets/my-sheet` | ✅ OAuth | 5 | ✅ |
| POST | `/api/sheets/create` | ✅ OAuth | 5 | ✅ |
| POST | `/api/sheets/link` | ✅ OAuth | 5 | ✅ |

---

## 技術棧

### 後端
- **框架**：FastAPI (Python 3.11+)
- **LLM**：OpenAI GPT-4 Turbo
- **TTS**：OpenAI TTS API
- **資料儲存**：Google Sheets (OAuth)
- **資料庫**：SQLite (本地) / Turso libSQL (生產)
- **認證**：JWT + API Token

### 前端
- **框架**：React + TypeScript + Vite
- **UI**：shadcn/ui (Radix UI + Tailwind CSS v4)
- **路由**：react-router-dom
- **圖表**：recharts
- **語音 STT**：Web Speech API（免費）
- **語音 TTS**：OpenAI TTS（付費，可選）+ Web Speech API（免費）
- **HTTP**：Axios

### 部署
- **後端**：GCP Cloud Run（asia-east1 台灣彰化）
- **前端**：Vercel（全球 CDN）
- **資料庫**：Turso libSQL（邊緣節點）
- **密鑰管理**：GCP Secret Manager

---

## 快速開始

```bash
# 開發模式（預設）
./start.sh
./start.sh dev

# 生產模式（本地測試生產設定）
./start.sh prod

# 或分別啟動
# 後端
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

- 前端：http://localhost:5173
- 後端 API：http://localhost:8000
- API 文件：http://localhost:8000/docs
- 健康檢查：http://localhost:8000/health

---

## 前端頁面

| 路徑 | 頁面 | 功能 |
|------|------|------|
| `/` | 記帳首頁 | 語音/文字記帳輸入 |
| `/stats` | 統計頁面 | 月度支出統計與圓餅圖 |
| `/query` | 查詢頁面 | 自然語言帳務查詢 |
| `/settings` | 設定頁面 | 帳戶管理、Token、語音設定 |
| `/privacy` | 隱私權政策 | 法律頁面 |
| `/terms` | 服務條款 | 法律頁面 |
| `/auth/callback` | OAuth 回調 | Google 登入處理 |

---

## 參考資源

- [task.md](../../task.md) - 完整專案規劃
- [README.md](../../README.md) - 專案說明
- [Siri 捷徑設定](../siri-shortcut-setup.md) - Siri 設定教學
