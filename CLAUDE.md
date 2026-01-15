# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 專案概述

語音記帳助手 - 整合 Siri 捷徑、LLM 和 Google Sheets 的智慧記帳系統。

**生產環境：**
- 前端：https://frontend-omega-eight-30.vercel.app
- 後端 API：https://ai-accounting-api-51386650140.asia-east1.run.app
- API 文件：https://ai-accounting-api-51386650140.asia-east1.run.app/docs

---

## 開發指令

### 一鍵啟動
```bash
./start.sh        # 開發環境（同時啟動前後端）
./start.sh prod   # 生產環境
```

### 後端指令
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload      # 開發（Port 8000）
uvicorn app.main:app --host 0.0.0.0 --port 8080  # 生產
```

### 前端指令
```bash
cd frontend
npm run dev       # 開發（Port 5173）
npm run build     # 構建（tsc + vite build）
npm run lint      # ESLint 檢查
npm run preview   # 預覽生產構建
```

---

## 架構概覽

```
使用者 (Web/Siri)
       ↓
Vercel (React SPA) ←→ Cloud Run (FastAPI)
                            ↓
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
           Turso        OpenAI API    Google APIs
          (libSQL)      (LLM/TTS)    (Sheets/OAuth)
```

### 技術棧
- **後端**：FastAPI + Python 3.11+、OpenAI GPT-4o-mini、SQLAlchemy
- **前端**：React 19 + TypeScript + Vite、shadcn/ui (Radix + Tailwind v4)
- **資料庫**：SQLite（開發）/ Turso libSQL（生產）
- **認證**：Google OAuth + JWT + API Token

### 後端結構
```
backend/app/
├── main.py           # FastAPI 入口
├── config.py         # Settings（環境變數）
├── api/              # 路由層
│   ├── auth.py       # OAuth + Token 認證
│   ├── accounting.py # 記帳 API
│   ├── sheets.py     # Sheet 管理
│   └── speech.py     # TTS API
├── database/
│   ├── engine.py     # SQLAlchemy 連線（Turso/SQLite 自動選擇）
│   ├── models.py     # User, GoogleToken, APIToken, UserSheet
│   └── crud.py       # CRUD 操作
├── services/         # 業務邏輯層
│   ├── openai_service.py
│   ├── user_sheets_service.py
│   ├── oauth_service.py
│   └── jwt_service.py
└── models/schemas.py # Pydantic 請求/回應模型
```

### 前端結構
```
frontend/src/
├── App.tsx                # 路由設定
├── contexts/AuthContext.tsx  # 認證狀態
├── pages/                 # 頁面元件
│   ├── HomePage.tsx       # 語音/文字記帳
│   ├── StatsPage.tsx      # 統計圖表
│   ├── QueryPage.tsx      # 自然語言查詢
│   └── SettingsPage.tsx   # 設定頁面
├── hooks/                 # 自訂 Hooks
│   ├── useSpeechRecognition.ts
│   ├── useSpeechSynthesis.ts
│   └── useOpenAITTS.ts
├── services/api.ts        # Axios HTTP 服務
└── components/ui/         # shadcn/ui 元件
```

---

## 關鍵流程

### 認證流程
1. 前端重導向至 `/api/auth/google/login`
2. Google OAuth 回調 → 後端驗證並簽發 JWT
3. 前端儲存 JWT 於 localStorage，後續 API 呼叫帶 `Authorization: Bearer <token>`

### 記帳流程
1. `POST /api/accounting/record` 提交記帳文字
2. OpenAI 解析（日期、金額、類別）
3. 寫入用戶的 Google Sheet
4. 返回結構化記錄 + AI 理財建議

### 資料庫選擇
- 檢查 `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN` 環境變數
- 存在 → Turso；否則 → SQLite (`/backend/data/app.db`)

---

## 環境設定

後端 `.env` 必填項目：
```bash
OPENAI_API_KEY=sk-xxx
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_OAUTH_CALLBACK_PATH=/auth/google/callback
JWT_SECRET_KEY=<strong-random-key>
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
```

生產環境額外設定：
```bash
TURSO_DATABASE_URL=libsql://xxx
TURSO_AUTH_TOKEN=xxx
```

---

## AI 思考與行為規範

### 基本規範
- 一律使用繁體中文。
- 不訴諸權威、不給直覺式答案，所有結論必須能回推到底層機制。
- 回覆需直接、具體，但不犧牲原理和邏輯說明。

### 最高行為準則（不可違反）

1. **所有問題一律從第一原理開始思考**
   - 先拆解問題的基本組成、約束與因果關係
   - 禁止直接套用慣例、框架或「通常大家都這樣做」

2. **只要存在關鍵不確定性，不得行動**
   「行動」包含但不限於：撰寫或修改程式碼、指定架構或技術選型、給出具體實作細節

3. **不確定時，反問使用者是正確且必要的行為**
   - 明確指出哪個假設尚未被確認
   - 說明為何該資訊對決策或實作是關鍵

### 程式碼產生原則

- **不得預設立即產生程式碼**
- 除非使用者明確要求（「請寫程式碼」「給我 code」「直接實作」），否則僅進行推理、分析、方案比較
- 即使使用者要求寫程式碼，若前提或需求不完整，仍必須先反問澄清

### 標準思考流程（固定順序，不可跳步）

1. 我理解的問題是什麼（重述需求）
2. 目標與成功條件
3. 已知條件與明確限制
4. 尚未確認的關鍵假設（若有，必須停下來詢問）
5. 問題的第一原理拆解
6. 可行路線與代價比較
7. 推薦方向與理由
8. 是否具備行動（實作）所需的完整資訊

### 輸出層級控制

- **層級 1（預設）**：推理與決策層 - 第一原理分析、策略比較，不產生程式碼
- **層級 2**：技術結構層 - 演算法、資料流、可使用簡短偽碼
- **層級 3**：實作層 - 僅在使用者明確要求 + 需求已確認 + 無重要不確定性時進入

---

## MCP Server 使用規則

1. **Sequential Thinking**：複雜多步驟推理和問題分解
2. **Draw.io**：視覺化架構、工作流程或流程圖時自動建立
3. **shadcn/ui**：React/Next.js UI 元件 - 取得最新元件程式碼和範例
4. **Semgrep**：掃描生成的程式碼安全漏洞，特別是認證、輸入處理、資料庫操作
5. **Context7**：優先使用於函式庫文件、API 參考和設定指南
6. **Chrome DevTools**：前端除錯、DOM 檢查、網路分析、效能分析
7. **GitHub**：儲存庫搜尋、檔案查找、Issue 追蹤
