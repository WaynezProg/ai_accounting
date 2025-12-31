# Phase 2：Siri 捷徑整合

## 目標

建立 API Token 認證機制，讓 Siri 捷徑可安全呼叫記帳 API。

---

## 前置條件

- [ ] Phase 1 完成
- [ ] 記帳 API 功能正常

---

## 任務清單

### 2.1 Token 認證機制

- [ ] 建立 Token 資料模型
  ```python
  class APIToken(BaseModel):
      token: str
      created_at: datetime
      expires_at: Optional[datetime]
      description: str  # 如 "Siri 捷徑"
  ```

- [ ] Token 儲存方式（Phase 5 前的簡化版）
  - 選項 A：環境變數固定 Token
  - 選項 B：SQLite 簡易儲存

- [ ] 實作 Bearer Token 驗證
  ```python
  # 依賴注入
  async def verify_token(
      authorization: str = Header(...)
  ) -> bool:
      # 驗證 Bearer Token
  ```

### 2.2 認證相關 API

- [ ] `POST /api/auth/token/generate`
  - 產生新的 API Token
  - 暫時可直接呼叫（Phase 5 後改為需 OAuth 登入）

- [ ] `GET /api/auth/token/verify`
  - 驗證 Token 是否有效

### 2.3 保護記帳 API

- [ ] 修改 `POST /api/accounting/record`
  - 加入 Token 驗證
  - 無 Token 或無效 Token 回傳 401

```python
@router.post("/record")
async def record_accounting(
    request: AccountingRequest,
    token_valid: bool = Depends(verify_token)
):
    ...
```

### 2.4 Siri 捷徑設定文件

- [ ] 建立 `docs/siri-shortcut-setup.md`
  - 捷徑建立步驟（含截圖說明）
  - API Token 取得方式
  - 捷徑設定參數

- [ ] 捷徑流程設計
  ```
  1. 觸發捷徑（語音或點擊）
  2. 聽寫輸入（Siri 內建 STT）
  3. 呼叫 API
     - URL: https://your-domain/api/accounting/record
     - Method: POST
     - Headers:
       - Content-Type: application/json
       - Authorization: Bearer <token>
     - Body: {"text": "聽寫內容"}
  4. 顯示/朗讀結果
  ```

### 2.5 本地測試

- [ ] 使用 ngrok 或類似工具暴露本地服務
- [ ] 在 iPhone 上測試 Siri 捷徑
- [ ] 驗證完整流程

---

## 完成條件

- [ ] API Token 機制運作正常
- [ ] 無 Token 無法呼叫記帳 API
- [ ] Siri 捷徑可成功記帳
- [ ] 設定文件完整

---

## 測試案例

```bash
# 無 Token（應回傳 401）
curl -X POST http://localhost:8000/api/accounting/record \
  -H "Content-Type: application/json" \
  -d '{"text": "午餐100元"}'

# 有 Token（應成功）
curl -X POST http://localhost:8000/api/accounting/record \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{"text": "午餐100元"}'
```

---

## 下一階段

完成後進入 [Phase 3：前端開發](./phase-3-frontend.md)
