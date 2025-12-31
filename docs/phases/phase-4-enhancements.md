# Phase 4：前端功能整合 ✅ 完成

## 目標

擴充前端功能，加入自然語音、統計圖表、查詢介面和 Token 管理。

---

## 前置條件

- [x] Phase 3 完成
- [x] 前端基礎功能可用

---

## 已完成項目

### 4.0 自然語音功能 ✅

- [x] 後端：新增 OpenAI TTS API 端點
  - `POST /api/speech/synthesize` - 文字轉語音
  - `GET /api/speech/voices` - 取得可用聲音列表
  - 使用 `gpt-4o-mini-tts` 模型（最新、最自然的中文支援）
  - 支援 11 種聲音：alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse
  - 支援語速調整 (0.25-4.0)

- [x] 前端：OpenAI TTS Hook (`useOpenAITTS`)
  - 呼叫後端 TTS API
  - 音訊播放控制
  - 載入狀態管理
  - 錯誤處理

- [x] 前端：設定管理 (`useSettings`)
  - 自然語音開關
  - 語音選擇
  - 語速調整
  - localStorage 持久化

- [x] 前端：UI 整合
  - 設定面板（齒輪按鈕展開）
  - 語音選擇 UI（6 個按鈕）
  - 播放狀態指示器（載入中/播放中）

**混合模式設計：**
- STT（語音輸入）：使用免費 Web Speech API
- TTS（語音輸出）：
  - 預設：OpenAI TTS（自然語音，付費）
  - 可選：Web Speech API（機器音，免費）

**成本估算：**
- OpenAI TTS：$0.015 / 1000 字元
- 每次記帳回饋約 50 字元 ≈ $0.00075
- 每月 300 次記帳 ≈ $0.23

---

### 4.1 統計頁面 ✅

- [x] 新增統計頁面路由 (`/stats`)
- [x] 安裝圖表套件 (`recharts`)
- [x] 統計頁面功能
  - 月份選擇器（左右箭頭切換）
  - 總支出顯示（大字體）
  - 類別圓餅圖 (PieChart)
  - 類別明細列表（金額、筆數、百分比）
  - 日均支出顯示

---

### 4.2 查詢介面 ✅

- [x] 新增查詢頁面 (`/query`)
- [x] 查詢功能
  - 文字輸入查詢
  - 語音輸入查詢（復用 useSpeechRecognition）
  - 顯示 LLM 回覆
  - 語音播放回覆
- [x] 查詢範例提示（快速點擊）
  - 「這個月花了多少錢？」
  - 「飲食類別佔比多少？」
  - 「哪個類別花最多？」
  - 「今天有記帳嗎？」
  - 「本月日均支出多少？」
- [x] 查詢歷史記錄

---

### 4.3 設定頁面與 Token 管理 ✅

- [x] 新增設定頁面 (`/settings`)
- [x] Token 管理功能
  - 顯示目前使用的 Token（部分遮蔽）
  - Token 驗證狀態顯示
  - 產生新 Token
  - 複製 Token 到剪貼簿
  - Siri 捷徑設定說明
- [x] 語音設定
  - 自然語音開關
  - 11 種語音選擇（含說明）
  - 語速調整滑桿
- [x] 重設設定功能
- [x] TTS 自動播放理財回饋（`feedback` 內容）

---

### 4.4 路由設定 ✅

- [x] 安裝 react-router-dom
- [x] 設定路由
  ```typescript
  const routes = [
    { path: '/', element: <HomePage /> },      // 記帳主頁
    { path: '/stats', element: <StatsPage /> }, // 統計頁面
    { path: '/query', element: <QueryPage /> }, // 查詢頁面
    { path: '/settings', element: <SettingsPage /> }, // 設定頁面
  ];
  ```
- [x] 底部導航列 (BottomNav)
  - 記帳（首頁）
  - 統計
  - 查詢
  - 設定
- [x] 頁面佈局 (AppLayout)
  - 固定頂部標題
  - 固定底部導航
  - 主內容區域滾動

---

### 4.5 狀態管理 ✅

- [x] 使用 React Hooks 管理狀態
  - `useSettings` - 全域設定（localStorage 持久化）
  - API Token 透過 localStorage 管理

---

## 已建立檔案

```
# 後端
backend/app/api/speech.py           # TTS API 端點

# 前端 - 頁面
frontend/src/pages/HomePage.tsx     # 記帳首頁
frontend/src/pages/StatsPage.tsx    # 統計頁面
frontend/src/pages/QueryPage.tsx    # 查詢頁面
frontend/src/pages/SettingsPage.tsx # 設定頁面
frontend/src/pages/index.ts         # 頁面導出

# 前端 - 佈局
frontend/src/components/layout/AppLayout.tsx  # 主佈局
frontend/src/components/layout/BottomNav.tsx  # 底部導航
frontend/src/components/layout/index.ts       # 佈局導出

# 前端 - Hooks
frontend/src/hooks/useOpenAITTS.ts  # OpenAI TTS Hook
frontend/src/hooks/useSettings.ts   # 設定管理 Hook

# 前端 - 服務
frontend/src/services/api.ts        # API 呼叫（含統計、查詢）

# 前端 - UI 元件
frontend/src/components/ui/switch.tsx
frontend/src/components/ui/label.tsx
```

---

## 完成條件

- [x] OpenAI TTS 自然語音功能可用
- [x] 可切換自然語音/機器音
- [x] 統計頁面可顯示圓餅圖
- [x] 查詢功能可用
- [x] Token 管理頁面可用
- [x] 頁面間導航順暢
- [x] 手機體驗良好（底部導航 + 響應式）

---

## 測試案例

### 自然語音
1. 進入設定頁面
2. 開啟「自然語音」開關
3. 選擇不同聲音（如 nova）
4. 調整語速
5. 回到首頁進行記帳
6. 確認語音回饋為自然 AI 聲音

### 統計頁面
1. 點擊底部「統計」導航
2. 確認顯示當月總支出
3. 使用左右箭頭切換月份
4. 確認圓餅圖正確顯示類別分佈
5. 確認類別明細顯示金額和百分比

### 查詢功能
1. 點擊底部「查詢」導航
2. 點擊範例問題或輸入自訂問題
3. 確認收到正確回覆
4. 點擊播放按鈕聽取語音回覆
5. 確認查詢歷史記錄正常

### Token 管理
1. 點擊底部「設定」導航
2. 輸入或產生新 Token
3. 確認 Token 驗證狀態
4. 點擊複製按鈕
5. 確認複製成功提示

---

## 下一階段

→ [Phase 5：Google OAuth](./phase-5-oauth.md) ✅ 已完成
