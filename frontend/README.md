# 語音記帳助手 - 前端

React + TypeScript + Vite + shadcn/ui 建立的語音記帳網頁應用程式。

## 功能特色

- **語音輸入**：使用 Web Speech API 進行語音識別（STT）
- **自然語音輸出**：使用 OpenAI TTS API（`gpt-4o-mini-tts` 模型，11 種聲音）
- **Google OAuth 登入**：使用 Google 帳號登入
- **Google Sheets 整合**：記帳資料儲存在用戶自己的 Google Sheet
- **統計圖表**：月度支出圓餅圖和類別明細
- **自然語言查詢**：用語音或文字查詢帳務狀況
- **理財回饋**：記帳後自動播放 AI 理財建議

## 頁面結構

| 路徑 | 頁面 | 功能 |
|------|------|------|
| `/` | 首頁 | 語音/文字記帳 |
| `/stats` | 統計 | 月度支出統計圖表 |
| `/query` | 查詢 | 自然語言查詢帳務 |
| `/settings` | 設定 | 帳號、Sheet、Token、語音設定 |

## 技術棧

- **框架**：React 18 + TypeScript
- **建置工具**：Vite
- **UI 元件**：shadcn/ui (Radix UI + Tailwind CSS v4)
- **圖表**：Recharts
- **路由**：React Router DOM
- **HTTP 客戶端**：Axios
- **語音**：
  - STT：Web Speech API
  - TTS：OpenAI TTS API（透過後端）

## 開發環境設定

### 前置需求

- Node.js 18+
- npm 或 yarn

### 安裝依賴

```bash
cd frontend
npm install
```

### 環境變數

建立 `.env` 檔案：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 啟動開發伺服器

```bash
npm run dev
```

開啟 http://localhost:5173

## 目錄結構

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui 元件
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── switch.tsx
│   │   │   ├── label.tsx
│   │   │   └── sonner.tsx
│   │   └── layout/          # 佈局元件
│   │       ├── AppLayout.tsx
│   │       └── BottomNav.tsx
│   ├── pages/               # 頁面元件
│   │   ├── HomePage.tsx     # 記帳首頁
│   │   ├── StatsPage.tsx    # 統計頁面
│   │   ├── QueryPage.tsx    # 查詢頁面
│   │   └── SettingsPage.tsx # 設定頁面
│   ├── hooks/               # 自訂 Hooks
│   │   ├── useSpeechRecognition.ts  # Web Speech API STT
│   │   ├── useSpeechSynthesis.ts    # Web Speech API TTS (備用)
│   │   ├── useOpenAITTS.ts          # OpenAI TTS
│   │   └── useSettings.ts           # 設定管理
│   ├── services/
│   │   └── api.ts           # API 呼叫封裝
│   ├── lib/
│   │   └── utils.ts         # 工具函數 (cn)
│   ├── App.tsx              # 路由設定
│   ├── index.css            # Tailwind CSS
│   └── main.tsx             # 入口
├── components.json          # shadcn/ui 設定
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

## API 服務

### 認證

- `getGoogleLoginUrl()` - 取得 Google OAuth 登入 URL
- `getCurrentUser()` - 取得當前用戶資訊
- `getAuthStatus()` - 檢查認證狀態
- `logout()` - 登出

### 記帳

- `createEntry(text)` - 建立記帳記錄
- `getMonthlyStats(year, month)` - 取得月度統計
- `queryAccounting(query)` - 自然語言查詢

### Sheet 管理

- `getMySheet()` - 取得用戶的 Sheet 資訊
- `listDriveSheets()` - 列出 Google Drive 中的 Sheets
- `selectSheet(sheetId, sheetName)` - 選擇現有 Sheet
- `createSheet(title)` - 建立新 Sheet

### Token 管理

- `generateNewToken(description)` - 產生 API Token
- `listAPITokens()` - 列出用戶的 Tokens
- `revokeAPIToken(tokenId)` - 撤銷 Token

### TTS

- `synthesizeSpeech(text, voice, speed)` - 文字轉語音
- `getAvailableVoices()` - 取得可用聲音列表

## 語音設定

### 可用聲音（11 種）

| ID | 名稱 | 描述 |
|-----|------|------|
| alloy | Alloy | 中性、平衡 |
| ash | Ash | 中性、沉穩 |
| ballad | Ballad | 抒情、溫柔 |
| coral | Coral | 女性、清晰 |
| echo | Echo | 男性、沉穩 |
| fable | Fable | 英式、敘事感 |
| onyx | Onyx | 男性、深沉 |
| nova | Nova | 女性、自然友善（推薦中文） |
| sage | Sage | 中性、穩重 |
| shimmer | Shimmer | 女性、清晰表達 |
| verse | Verse | 中性、自然 |

### 語速調整

- 範圍：0.25 - 4.0
- 預設：1.0

## 建置生產版本

```bash
npm run build
```

產出檔案在 `dist/` 目錄。

## 瀏覽器相容性

| 功能 | Chrome | Safari | Firefox | Edge |
|------|--------|--------|---------|------|
| STT | ✅ | ✅ (限制) | ❌ | ✅ |
| TTS (OpenAI) | ✅ | ✅ | ✅ | ✅ |
| TTS (Web API) | ✅ | ✅ | ✅ | ✅ |

注意：Web Speech API 的語音識別在 Firefox 不支援，建議使用 Chrome 或 Safari。
