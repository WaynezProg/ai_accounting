# Phase 5：Google OAuth 2.0 🔲 待開發

## 目標

實作用戶登入機制，讓每個用戶使用自己的 Google Sheet。

---

## 前置條件

- [ ] Phase 4 完成
- [ ] GCP 專案已設定 OAuth 2.0 憑證
- [ ] 授權重新導向 URI 已設定

---

## 任務清單

### 5.1 GCP OAuth 設定

- [ ] 建立 OAuth 2.0 憑證（Web Application 類型）
- [ ] 設定授權重新導向 URI
  - 開發：`http://localhost:8000/api/auth/google/callback`
  - 生產：`https://your-domain/api/auth/google/callback`
- [ ] 下載憑證 JSON
- [ ] 設定 OAuth 同意畫面
  - 應用程式名稱
  - 支援電子郵件
  - 授權範圍（Sheets、Drive）

### 5.2 資料庫設定

- [ ] 安裝依賴
  ```bash
  pip install aiosqlite sqlalchemy[asyncio]
  ```

- [ ] 建立 SQLite 資料庫結構
  ```python
  # models/database.py
  class User(Base):
      id: str  # Google User ID
      email: str
      name: str
      created_at: datetime

  class GoogleToken(Base):
      user_id: str (FK)
      access_token: str (encrypted)
      refresh_token: str (encrypted)
      expires_at: datetime

  class APIToken(Base):
      token_hash: str
      user_id: str (FK)
      description: str
      created_at: datetime
      expires_at: Optional[datetime]
      is_active: bool

  class UserSheet(Base):
      user_id: str (FK)
      sheet_id: str
      sheet_url: str
  ```

- [ ] 實作資料庫服務
  - `create_user()`
  - `get_user()`
  - `save_google_token()`
  - `get_google_token()`
  - `refresh_token_if_needed()`

### 5.3 OAuth 認證流程

- [ ] `GET /api/auth/google/login`
  - 產生 OAuth URL（含 state 參數）
  - 重導向至 Google 登入

- [ ] `GET /api/auth/google/callback`
  - 驗證 state 參數
  - 交換 Authorization Code 為 Token
  - 取得用戶資訊
  - 建立/更新用戶資料
  - 儲存 Google Token
  - 重導向至前端（帶 Session Token）

- [ ] `POST /api/auth/logout`
  - 清除 Session
  - 可選：撤銷 Google Token

- [ ] `GET /api/auth/me`
  - 回傳當前登入用戶資訊

### 5.4 Session / JWT 管理

- [ ] 選擇認證方式
  - 選項 A：Cookie-based Session（適合 SSR）
  - 選項 B：JWT Token（適合 SPA）

- [ ] 實作認證中介層
  ```python
  async def get_current_user(
      token: str = Depends(oauth2_scheme)
  ) -> User:
      # 驗證 JWT 並回傳用戶
  ```

- [ ] 支援兩種認證方式
  - OAuth Session（網頁登入用戶）
  - API Token（Siri 捷徑）

### 5.5 用戶專屬 Sheet

- [ ] 首次登入時自動建立 Sheet
  ```python
  async def create_user_sheet(user: User, credentials):
      # 使用用戶的 OAuth Token 建立 Sheet
      # 設定 Sheet 結構（標題列）
      # 儲存 Sheet ID 至資料庫
  ```

- [ ] 修改 GoogleSheetsService
  - 接受用戶 OAuth Token（而非 Service Account）
  - 操作用戶自己的 Sheet
  - 處理 Token 刷新

### 5.6 前端 OAuth 整合

- [ ] 登入按鈕
  - 點擊後導向 `/api/auth/google/login`

- [ ] 處理 OAuth 回調
  - 從 URL 取得 Token
  - 儲存至 localStorage / Cookie
  - 導向主頁面

- [ ] 認證狀態管理
  - Context 或 Zustand
  - 自動刷新 Token
  - 登入狀態持久化

- [ ] 登出功能
  - 清除本地 Token
  - 呼叫後端登出 API

- [ ] 條件渲染
  - 未登入：顯示登入按鈕
  - 已登入：顯示用戶資訊 + 登出按鈕

### 5.7 API Token 與 OAuth 整合

- [ ] 修改 Token 產生邏輯
  - 需登入後才能產生
  - Token 綁定用戶 ID

- [ ] 修改 Token 驗證邏輯
  - Token 查詢時取得對應用戶
  - 記帳 API 使用用戶的 Sheet

- [ ] 記帳 API 支援兩種認證
  - OAuth Session（網頁）→ 用戶的 Sheet
  - API Token（Siri）→ Token 綁定用戶的 Sheet

### 5.8 資料遷移

- [ ] 遷移現有 Token（JSON → SQLite）
- [ ] 遷移腳本

---

## 完成條件

- [ ] 可使用 Google 帳號登入
- [ ] 每個用戶有自己的 Sheet
- [ ] Google Token 正確儲存與刷新
- [ ] Siri 捷徑仍可使用（透過 API Token）
- [ ] 前端登入/登出功能正常

---

## 安全性注意事項

- [ ] Token 加密儲存
- [ ] HTTPS 強制（生產環境）
- [ ] CSRF 防護
- [ ] state 參數驗證（防止 CSRF）
- [ ] 敏感資訊不外洩（Token 不顯示在 URL）

---

## 環境變數更新

```bash
# 新增
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
JWT_SECRET_KEY=random-secret-for-jwt
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

---

## 測試案例

1. 點擊 Google 登入
2. 完成 OAuth 授權
3. 確認自動建立 Sheet
4. 記帳並確認寫入用戶的 Sheet
5. 產生 API Token
6. 用 API Token 呼叫記帳 API
7. 確認寫入同一用戶的 Sheet
8. 登出並確認狀態清除

---

## 下一階段

→ [Phase 6：部署上線](./phase-6-deployment.md) 🔲 待開發
