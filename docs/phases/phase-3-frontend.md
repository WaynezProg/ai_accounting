# Phase 3：前端基礎建設 ✅ 完成

## 目標

建立網頁版記帳介面，支援語音輸入與輸出。

---

## 前置條件

- [x] Phase 2 完成
- [x] 後端 API 穩定運作

---

## 任務清單

### 3.1 前端專案初始化

- [x] 建立 React + TypeScript + Vite 專案
  ```bash
  cd frontend
  npm create vite@latest . -- --template react-ts
  ```

- [x] 安裝依賴
  ```bash
  npm install axios
  npm install -D @tailwindcss/vite
  ```

- [x] 設定 shadcn/ui (Tailwind CSS v4)
  ```bash
  npx shadcn@latest init -d
  ```

- [x] 建立目錄結構
  ```
  frontend/
  ├── src/
  │   ├── components/ui/      # shadcn/ui 元件
  │   │   ├── button.tsx
  │   │   ├── card.tsx
  │   │   ├── input.tsx
  │   │   └── sonner.tsx
  │   ├── services/
  │   │   └── api.ts          # API 呼叫封裝
  │   ├── hooks/
  │   │   ├── useSpeechRecognition.ts
  │   │   └── useSpeechSynthesis.ts
  │   ├── lib/
  │   │   └── utils.ts        # cn() helper
  │   ├── App.tsx
  │   ├── index.css
  │   └── main.tsx
  ├── components.json
  ├── package.json
  └── vite.config.ts
  ```

### 3.2 API 服務層

- [x] 建立 `src/services/api.ts`
  - Token 管理（localStorage）
  - axios interceptors（自動加入 Authorization header）
  - createEntry - 記帳 API
  - healthCheck - 健康檢查
  - 完整 TypeScript 型別定義

### 3.3 語音輸入 (STT)

- [x] 建立 `useSpeechRecognition` Hook
  - Web Speech API 整合
  - 支援繁體中文 (zh-TW)
  - 回傳：transcript, isListening, startListening, stopListening, error, isSupported

- [x] 整合至主頁面
  - 麥克風按鈕
  - 錄音狀態指示（紅點動畫）
  - 即時顯示識別文字
  - 瀏覽器相容性檢查

### 3.4 語音輸出 (TTS)

- [x] 建立 `useSpeechSynthesis` Hook
  - Web Speech API 整合
  - 支援繁體中文 (zh-TW)
  - 回傳：speak, cancel, isSpeaking, voices, isSupported

- [x] 整合至主頁面
  - 記帳成功後自動播放回饋
  - 播放狀態指示

### 3.5 主頁面開發

- [x] 安裝需要的 shadcn/ui 元件
  ```bash
  npx shadcn@latest add button card input sonner -y
  ```

- [x] 建立主頁面 `App.tsx`
  - Token 輸入區（儲存至 localStorage）
  - 語音輸入區（麥克風按鈕）
  - 文字輸入區（備用）
  - 送出按鈕
  - 結果顯示區

- [x] 記帳結果顯示
  - 顯示解析結果（時間、金額、類別等）
  - 使用中文欄位名稱對應後端
  - 理財回饋顯示
  - 語音播放回饋

### 3.6 UI/UX 設計

- [x] 響應式佈局（max-w-md 置中）
- [x] 載入狀態（按鈕顯示「處理中...」）
- [x] 錯誤提示（Sonner Toast）
- [ ] 深色模式支援（CSS 變數已準備，待加入切換）

### 3.7 環境變數與啟動腳本

- [x] 支援 `VITE_API_BASE_URL` 環境變數（預設 http://localhost:8000）
- [x] 更新 `start.sh` 同時啟動前後端

---

## 完成條件

- [x] 前端可正常啟動 (`npm run dev`)
- [x] 語音輸入可識別中文
- [x] 可成功呼叫後端 API 記帳
- [x] 結果可語音播放
- [ ] 手機瀏覽器可正常使用（待測試）

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

注意：Web Speech API 在不同瀏覽器支援度不同，已加入相容性檢查與提示。

---

## 已建立檔案

```
frontend/
├── src/
│   ├── components/ui/
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── sonner.tsx
│   ├── hooks/
│   │   ├── useSpeechRecognition.ts
│   │   └── useSpeechSynthesis.ts
│   ├── services/
│   │   └── api.ts
│   ├── lib/
│   │   └── utils.ts
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
├── components.json
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
└── vite.config.ts
```

---

## 啟動方式

```bash
# 同時啟動前後端
./start.sh

# 或單獨啟動前端
cd frontend
npm run dev
```

- 前端：http://localhost:5173
- 後端 API：http://localhost:8000
- API 文件：http://localhost:8000/docs

---

## 下一階段

→ [Phase 4：前端功能整合](./phase-4-enhancements.md) 🔲 待開發
