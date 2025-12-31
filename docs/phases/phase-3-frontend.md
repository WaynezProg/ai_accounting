# Phase 3：前端基礎建設 🔲 待開發

## 目標

建立網頁版記帳介面，支援語音輸入與輸出。

---

## 前置條件

- [x] Phase 2 完成
- [x] 後端 API 穩定運作

---

## 任務清單

### 3.1 前端專案初始化

- [ ] 建立 React + TypeScript + Vite 專案
  ```bash
  cd frontend
  npm create vite@latest . -- --template react-ts
  ```

- [ ] 安裝依賴
  ```bash
  npm install axios
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```

- [ ] 設定 shadcn/ui
  ```bash
  npx shadcn@latest init
  ```

- [ ] 建立目錄結構
  ```
  frontend/
  ├── src/
  │   ├── components/
  │   │   ├── ui/              # shadcn/ui 元件
  │   │   ├── VoiceRecorder.tsx
  │   │   ├── VoicePlayer.tsx
  │   │   └── AccountingResult.tsx
  │   ├── services/
  │   │   └── api.ts           # API 呼叫封裝
  │   ├── hooks/
  │   │   ├── useSpeechRecognition.ts
  │   │   └── useSpeechSynthesis.ts
  │   ├── lib/
  │   │   └── utils.ts         # cn() helper
  │   ├── types/
  │   │   └── index.ts         # TypeScript 型別
  │   ├── App.tsx
  │   └── main.tsx
  ├── components.json
  ├── package.json
  ├── tailwind.config.js
  ├── .env.example
  └── vite.config.ts
  ```

### 3.2 API 服務層

- [ ] 建立 `src/services/api.ts`
  ```typescript
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  export const accountingApi = {
    record: async (text: string, token: string) => { ... },
    getStats: async (token: string, month?: string) => { ... },
    query: async (query: string, token: string) => { ... },
    getCategories: async () => { ... },
  };

  export const authApi = {
    generateToken: async (description: string) => { ... },
    verifyToken: async (token: string) => { ... },
  };
  ```

- [ ] 設定 axios interceptors（錯誤處理）

### 3.3 語音輸入 (STT)

- [ ] 建立 `useSpeechRecognition` Hook
  ```typescript
  const useSpeechRecognition = () => {
    // Web Speech API
    // 回傳：transcript, isListening, startListening, stopListening, error
  };
  ```

- [ ] 建立 `VoiceRecorder` 元件
  - 麥克風按鈕
  - 錄音狀態指示（動畫）
  - 即時顯示識別文字
  - 瀏覽器相容性檢查

### 3.4 語音輸出 (TTS)

- [ ] 建立 `useSpeechSynthesis` Hook
  ```typescript
  const useSpeechSynthesis = () => {
    // Web Speech API
    // 回傳：speak, stop, isSpeaking
  };
  ```

- [ ] 建立 `VoicePlayer` 元件
  - 播放/停止按鈕
  - 播放狀態指示

### 3.5 主頁面開發

- [ ] 安裝需要的 shadcn/ui 元件
  ```bash
  npx shadcn@latest add button card input toast
  ```

- [ ] 建立主頁面 `App.tsx`
  - Token 輸入區（首次使用）
  - 語音輸入區
  - 文字輸入區（備用）
  - 送出按鈕
  - 結果顯示區

- [ ] 建立 `AccountingResult` 元件
  - 顯示解析結果（時間、金額、類別等）
  - 成功/失敗狀態
  - 理財回饋顯示
  - 語音播放回饋

### 3.6 UI/UX 設計

- [ ] 響應式佈局（手機優先）
- [ ] 載入狀態（Skeleton / Spinner）
- [ ] 錯誤提示（Toast）
- [ ] 深色模式支援（可選）

### 3.7 環境變數

- [ ] 建立 `frontend/.env.example`
  ```bash
  VITE_API_BASE_URL=http://localhost:8000
  ```

---

## 完成條件

- [ ] 前端可正常啟動 (`npm run dev`)
- [ ] 語音輸入可識別中文
- [ ] 可成功呼叫後端 API 記帳
- [ ] 結果可語音播放
- [ ] 手機瀏覽器可正常使用

---

## 測試案例

1. 開啟網頁，輸入 API Token
2. 點擊麥克風
3. 說「午餐吃滷肉飯 80 元」
4. 確認文字識別正確
5. 點擊送出
6. 確認顯示記帳結果
7. 確認語音播放結果

---

## 瀏覽器相容性

| 功能 | Chrome | Safari | Firefox | Edge |
|------|--------|--------|---------|------|
| STT | ✅ | ✅ (限制) | ❌ | ✅ |
| TTS | ✅ | ✅ | ✅ | ✅ |

注意：Web Speech API 在不同瀏覽器支援度不同，需加入相容性檢查與提示。

---

## 下一階段

→ [Phase 4：前端功能整合](./phase-4-enhancements.md) 🔲 待開發
