# Phase 1：後端核心功能

## 目標

強化後端 API，確保記帳核心流程穩定可用。

---

## 前置條件

- [ ] Phase 0 完成
- [ ] 後端可正常啟動

---

## 任務清單

### 1.1 Pydantic 資料模型

- [ ] 建立請求/回應模型 (`backend/app/models/schemas.py`)
  ```python
  # 記帳請求
  class AccountingRequest(BaseModel):
      text: str  # 語音轉文字內容

  # 記帳記錄
  class AccountingRecord(BaseModel):
      date: str
      time: str
      amount: float
      category: str
      name: str
      currency: str = "TWD"
      payment_method: Optional[str] = None

  # 記帳回應
  class AccountingResponse(BaseModel):
      success: bool
      record: AccountingRecord
      message: str
  ```

### 1.2 OpenAI 服務優化

- [ ] 建立 `OpenAIService` 類別
- [ ] 優化 Prompt 設計
  - 明確輸出 JSON 結構
  - 處理模糊輸入（如「剛剛」→當前時間）
  - 預設類別對應
- [ ] 錯誤處理與重試機制
- [ ] Token 使用量追蹤（可選）

### 1.3 Google Sheets 服務優化

- [ ] 建立 `GoogleSheetsService` 類別
- [ ] 實作功能：
  - `write_record()` - 寫入單筆記錄
  - `get_all_records()` - 讀取所有記錄（供統計用）
  - `init_sheet()` - 初始化 Sheet 結構（標題列）
- [ ] 處理 API 錯誤
- [ ] 連線池/快取優化（可選）

### 1.4 記帳 API 端點

- [ ] `POST /api/accounting/record`
  - 輸入：`{"text": "中午吃排骨便當120元"}`
  - 處理：LLM 解析 → 寫入 Sheets
  - 輸出：結構化記錄 + 確認訊息
- [ ] `GET /api/accounting/categories`
  - 回傳預設類別清單
- [ ] `GET /health`
  - 健康檢查

### 1.5 預設類別定義

- [ ] 建立 `backend/app/utils/categories.py`
  ```python
  DEFAULT_CATEGORIES = [
      "飲食",
      "交通",
      "娛樂",
      "購物",
      "居住",
      "醫療",
      "教育",
      "其他"
  ]
  ```

### 1.6 錯誤處理

- [ ] 全域錯誤處理器
- [ ] 自訂例外類別
- [ ] 統一錯誤回應格式
  ```python
  {
      "success": False,
      "error": {
          "code": "PARSE_ERROR",
          "message": "無法解析記帳內容"
      }
  }
  ```

### 1.7 日誌系統

- [ ] 設定 logging
- [ ] 記錄關鍵操作（API 請求、LLM 呼叫、Sheets 寫入）

---

## 完成條件

- [ ] 記帳 API 可正常處理各種輸入
- [ ] 錯誤情況有適當處理
- [ ] 日誌可追蹤問題
- [ ] API 文件自動生成（FastAPI Swagger）

---

## 測試案例

```bash
# 基本記帳
curl -X POST http://localhost:8000/api/accounting/record \
  -H "Content-Type: application/json" \
  -d '{"text": "中午吃排骨便當120元"}'

# 複雜輸入
curl -X POST http://localhost:8000/api/accounting/record \
  -H "Content-Type: application/json" \
  -d '{"text": "剛剛搭捷運花了25塊用悠遊卡"}'
```

---

## 下一階段

完成後進入 [Phase 2：Siri 捷徑整合](./phase-2-siri-integration.md)
