# Phase 2：Siri 捷徑整合 ✅ 已完成

## 目標

建立 API Token 認證機制，讓 Siri 捷徑可安全呼叫記帳 API。

---

## 前置條件 ✅

- [x] Phase 1 完成
- [x] 記帳 API 功能正常

---

## 完成項目

### 2.1 Token 認證機制 ✅

- [x] 建立 Token 資料模型 (`backend/app/models/token.py`)
  ```python
  class APIToken(BaseModel):
      token: str
      description: str = ""
      created_at: datetime
      expires_at: Optional[datetime] = None
      is_active: bool = True

      def is_valid(self) -> bool:
          # 檢查 Token 是否有效
  ```

- [x] Token 儲存方式（Phase 5 前的簡化版）
  - 使用 JSON 檔案儲存 (`backend/data/tokens.json`)
  - `TokenStore` 類別管理 CRUD 操作

- [x] 實作 Bearer Token 驗證 (`backend/app/utils/auth.py`)
  ```python
  async def verify_token(
      credentials: HTTPAuthorizationCredentials = Depends(security)
  ) -> bool:
      # 驗證 Bearer Token
  ```

### 2.2 認證相關 API ✅

- [x] `POST /api/auth/token/generate`
  - 產生新的 API Token
  - 支援設定過期時間
  - 暫時可直接呼叫（Phase 5 後改為需 OAuth 登入）

- [x] `GET /api/auth/token/verify`
  - 驗證 Token 是否有效

- [x] `GET /api/auth/status`
  - 檢查認證狀態

### 2.3 保護記帳 API ✅

- [x] 修改 `POST /api/accounting/record` - 加入 Token 驗證
- [x] 修改 `GET /api/accounting/stats` - 加入 Token 驗證
- [x] 修改 `POST /api/accounting/query` - 加入 Token 驗證
- [x] 無 Token 或無效 Token 回傳 401

```python
@router.post("/record")
async def record_accounting(
    request: AccountingRequest,
    token_valid: bool = Depends(verify_token)
):
    ...
```

### 2.4 Siri 捷徑設定文件 ✅

- [x] 建立 `docs/siri-shortcut-setup.md`
  - 捷徑建立步驟
  - API Token 取得方式
  - 捷徑設定參數
  - 錯誤排除說明

- [x] 捷徑流程設計
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

### 2.5 本地測試 ✅

- [x] 後端 API 測試通過
- [x] Token 產生/驗證功能正常
- [ ] ngrok 暴露本地服務（用戶需自行設定）
- [ ] iPhone Siri 捷徑測試（用戶需自行測試）

---

## 完成條件 ✅

- [x] API Token 機制運作正常
- [x] 無 Token 無法呼叫記帳 API（回傳 401）
- [x] 設定文件完整
- [ ] Siri 捷徑實際測試（需用戶自行驗證）

---

## 測試案例 ✅

```bash
# 產生 Token
curl -X POST http://localhost:8000/api/auth/token/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "Siri 捷徑"}'

# 無 Token（應回傳 401）
curl -X POST http://localhost:8000/api/accounting/record \
  -H "Content-Type: application/json" \
  -d '{"text": "午餐100元"}'

# 有 Token（應成功）
curl -X POST http://localhost:8000/api/accounting/record \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{"text": "午餐100元"}'

# 驗證 Token
curl http://localhost:8000/api/auth/token/verify \
  -H "Authorization: Bearer your-token-here"
```

---

## 下一階段

→ [Phase 3：前端基礎建設](./phase-3-frontend.md) 🔲 待開發
