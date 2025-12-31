# Phase 4：前端功能整合 🔲 待開發

## 目標

擴充前端功能，加入統計圖表、查詢介面和 Token 管理。

---

## 前置條件

- [ ] Phase 3 完成
- [ ] 前端基礎功能可用

---

## 已完成的後端功能

> 以下 API 在 Phase 1 已實作完成，本階段專注於前端整合

- ✅ `GET /api/accounting/stats` - 月度統計
- ✅ `POST /api/accounting/query` - 自然語言查詢
- ✅ 記帳回應包含 `feedback` 理財回饋

---

## 任務清單

### 4.1 統計頁面

- [ ] 新增統計頁面路由 (`/stats`)
- [ ] 安裝圖表套件
  ```bash
  npm install recharts
  ```

- [ ] 統計頁面功能
  - 月份選擇器
  - 總支出顯示（大字體）
  - 類別圓餅圖 (PieChart)
  - 類別明細列表（金額、筆數）
  - 與上月比較（可選）

- [ ] 統計頁面元件
  ```typescript
  // components/stats/
  ├── MonthPicker.tsx      // 月份選擇
  ├── TotalExpense.tsx     // 總支出卡片
  ├── CategoryPieChart.tsx // 圓餅圖
  └── CategoryList.tsx     // 類別明細
  ```

### 4.2 查詢介面

- [ ] 新增查詢區塊或頁面
- [ ] 查詢功能
  - 文字輸入查詢
  - 語音輸入查詢（復用 useSpeechRecognition）
  - 顯示 LLM 回覆
  - 語音播放回覆

- [ ] 查詢範例提示
  - 「這個月花了多少錢？」
  - 「飲食類別佔比多少？」
  - 「哪個類別花最多？」

### 4.3 Token 管理頁面

- [ ] 新增設定頁面 (`/settings`)
- [ ] Token 管理功能
  - 顯示目前使用的 Token（部分遮蔽）
  - 產生新 Token
  - 複製 Token 到剪貼簿
  - Token 使用說明（for Siri）

### 4.4 路由設定

- [ ] 安裝 react-router-dom
  ```bash
  npm install react-router-dom
  ```

- [ ] 設定路由
  ```typescript
  const routes = [
    { path: '/', element: <HomePage /> },      // 記帳主頁
    { path: '/stats', element: <StatsPage /> }, // 統計頁面
    { path: '/settings', element: <SettingsPage /> }, // 設定頁面
  ];
  ```

- [ ] 底部導航列 (BottomNav)
  - 記帳（首頁）
  - 統計
  - 設定

### 4.5 狀態管理

- [ ] 選擇狀態管理方案
  - 選項 A：React Context（簡單場景）
  - 選項 B：Zustand（中等複雜度）

- [ ] 全域狀態
  - API Token
  - 用戶偏好設定（如深色模式）

### 4.6 UI 優化

- [ ] 安裝更多 shadcn/ui 元件
  ```bash
  npx shadcn@latest add select tabs dialog
  ```

- [ ] 錯誤邊界 (Error Boundary)
- [ ] 離線提示
- [ ] PWA 支援（可選）

---

## 完成條件

- [ ] 統計頁面可顯示圓餅圖
- [ ] 查詢功能可用
- [ ] Token 管理頁面可用
- [ ] 頁面間導航順暢
- [ ] 手機體驗良好

---

## 測試案例

### 統計頁面
1. 切換到統計頁面
2. 選擇不同月份
3. 確認圓餅圖正確顯示
4. 確認類別明細正確

### 查詢功能
1. 輸入「這個月飲食花多少？」
2. 確認收到正確回覆
3. 點擊語音播放
4. 確認語音播放正常

### Token 管理
1. 進入設定頁面
2. 點擊產生新 Token
3. 確認 Token 顯示
4. 點擊複製按鈕
5. 確認複製成功

---

## 下一階段

→ [Phase 5：Google OAuth](./phase-5-oauth.md) 🔲 待開發
