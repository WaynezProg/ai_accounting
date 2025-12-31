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
| 4 | [前端功能整合](./phase-4-enhancements.md) | 🔲 待開發 | 統計圖表、查詢介面 |
| 5 | [Google OAuth](./phase-5-oauth.md) | 🔲 待開發 | 用戶登入、個人 Sheet |
| 6 | [部署上線](./phase-6-deployment.md) | 🔲 待開發 | GCP Cloud Run、CI/CD |

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
   │         │         │         │         │         │         └─ 上線
   │         │         │         │         │         └─ 多用戶支援
   │         │         │         │         └─ 前端功能完整
   │         │         │         └─ 網頁版可用 ← 目前進度
   │         │         └─ Siri 可用
   │         └─ API 可用
   └─ 專案結構就緒
```

---

## 快速里程碑

| 里程碑 | 完成 Phase | 可用功能 | 狀態 |
|--------|-----------|----------|:----:|
| MVP（最小可用） | 0, 1, 2 | Siri 語音記帳 | ✅ |
| 網頁版基礎 | + 3 | 網頁語音記帳 | ✅ |
| 網頁版完整 | + 4 | 統計圖表、查詢介面 | 🔲 |
| 多用戶 | + 5 | 用戶自己的 Sheet | 🔲 |
| 生產就緒 | + 6 | 正式上線 | 🔲 |

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
- ✅ Web Speech API 語音輸出 (TTS)
- ✅ 繁體中文 (zh-TW) 支援
- ✅ 瀏覽器相容性檢查

**UI/UX：**
- ✅ Token 輸入區（localStorage 儲存）
- ✅ 語音/文字輸入區
- ✅ 記帳結果顯示（含理財回饋）
- ✅ 響應式佈局
- ✅ Toast 通知提示

**啟動腳本：**
- ✅ start.sh 同時啟動前後端

---

## API 端點總覽

| 方法 | 路徑 | 認證 | Phase | 狀態 |
|------|------|:----:|:-----:|:----:|
| GET | `/health` | ❌ | 0 | ✅ |
| POST | `/api/accounting/record` | ✅ Token | 1 | ✅ |
| GET | `/api/accounting/categories` | ❌ | 1 | ✅ |
| GET | `/api/accounting/stats` | ✅ Token | 1 | ✅ |
| POST | `/api/accounting/query` | ✅ Token | 1 | ✅ |
| POST | `/api/auth/token/generate` | ❌* | 2 | ✅ |
| GET | `/api/auth/token/verify` | ✅ Token | 2 | ✅ |
| GET | `/api/auth/status` | ✅ Token | 2 | ✅ |
| GET | `/api/auth/google/login` | ❌ | 5 | 🔲 |
| GET | `/api/auth/google/callback` | ❌ | 5 | 🔲 |
| POST | `/api/auth/logout` | ✅ OAuth | 5 | 🔲 |

> *註：Phase 5 後 `/api/auth/token/generate` 需要 OAuth 登入

---

## 技術棧

### 後端（已完成）
- **框架**：FastAPI (Python 3.11+)
- **LLM**：OpenAI GPT-4 Turbo
- **資料儲存**：Google Sheets (Service Account)
- **認證**：Bearer Token (JSON 儲存)

### 前端（已完成）
- **框架**：React + TypeScript + Vite
- **UI**：shadcn/ui (Radix UI + Tailwind CSS v4)
- **語音**：Web Speech API
- **HTTP**：Axios

### 部署（待開發）
- **後端**：GCP Cloud Run
- **前端**：Firebase Hosting / Vercel
- **資料庫**：Cloud SQL (PostgreSQL)
- **CI/CD**：Cloud Build

---

## 快速開始

```bash
# 同時啟動前後端
./start.sh

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

## 參考資源

- [task.md](../../task.md) - 完整專案規劃
- [README.md](../../README.md) - 專案說明
- [Siri 捷徑設定](../siri-shortcut-setup.md) - Siri 設定教學
