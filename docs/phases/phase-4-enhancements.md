# Phase 4：功能補強

## 目標

新增統計查詢與理財回饋功能，提升使用體驗。

---

## 前置條件

- [ ] Phase 3 完成
- [ ] 前後端整合正常運作

---

## 任務清單

### 4.1 統計查詢 API

- [ ] `GET /api/accounting/stats`
  - 查詢參數：`month` (如 `2024-01`)
  - 回傳：
    ```json
    {
      "success": true,
      "data": {
        "month": "2024-01",
        "total": 15000,
        "by_category": {
          "飲食": 5000,
          "交通": 2000,
          "娛樂": 3000
        },
        "record_count": 45
      }
    }
    ```

- [ ] 實作 `GoogleSheetsService.get_monthly_stats()`
  - 讀取指定月份記錄
  - 依類別彙總
  - 計算總額

### 4.2 帳務查詢 API

- [ ] `POST /api/accounting/query`
  - 輸入：`{"query": "這個月花了多少錢？"}`
  - 處理：LLM 理解問題 → 查詢資料 → 生成回答
  - 輸出：自然語言回覆

- [ ] 實作查詢邏輯
  ```python
  async def query_accounting(query: str):
      # 1. 取得相關統計資料
      stats = await sheets_service.get_stats()

      # 2. 組合 Prompt
      prompt = f"""
      用戶問題：{query}

      統計資料：
      - 本月總支出：{stats.total}
      - 類別明細：{stats.by_category}

      請用自然語言回答用戶問題。
      """

      # 3. 呼叫 LLM
      response = await openai_service.chat(prompt)
      return response
  ```

### 4.3 理財回饋功能

- [ ] 在記帳成功後自動生成回饋
  - 修改 `POST /api/accounting/record` 回應
  - 加入 `feedback` 欄位

- [ ] 回饋邏輯設計
  ```python
  async def generate_feedback(record, monthly_stats):
      prompt = f"""
      用戶剛記錄：{record.category} {record.amount}元

      本月統計：
      - 總支出：{monthly_stats.total}
      - {record.category}類別已花費：{monthly_stats.by_category.get(record.category, 0)}

      請給出簡短的理財建議（1-2句話）。
      """
      return await openai_service.chat(prompt)
  ```

- [ ] 回饋範例：
  - 「已記錄午餐 120 元。本月飲食類別已消費 3,500 元，佔總支出 35%。」
  - 「已記錄交通費 25 元。本月交通支出穩定，繼續保持！」

### 4.4 前端統計頁面

- [ ] 新增統計頁面路由
- [ ] 安裝圖表套件（可選）
  ```bash
  npm install recharts
  ```

- [ ] 統計頁面功能
  - 月份選擇器
  - 總支出顯示
  - 類別圓餅圖
  - 類別明細列表

### 4.5 前端查詢功能

- [ ] 新增查詢輸入區
- [ ] 支援語音查詢
- [ ] 顯示 LLM 回覆
- [ ] 語音播放回覆

### 4.6 Prompt 優化

- [ ] 優化記帳解析 Prompt
  - 提高準確度
  - 減少 Token 使用

- [ ] 優化理財回饋 Prompt
  - 回覆更自然
  - 建議更實用

---

## 完成條件

- [ ] 統計 API 正常運作
- [ ] 查詢 API 可理解各種問題
- [ ] 記帳後有理財回饋
- [ ] 前端可查看統計

---

## 測試案例

```bash
# 統計查詢
curl http://localhost:8000/api/accounting/stats?month=2024-01

# 帳務查詢
curl -X POST http://localhost:8000/api/accounting/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token" \
  -d '{"query": "這個月飲食花了多少？"}'
```

---

## 下一階段

完成後進入 [Phase 5：Google OAuth 2.0](./phase-5-oauth.md)
