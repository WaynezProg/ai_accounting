# Phase 5：Google OAuth 2.0 ✅ 完成

## 目標

實作用戶登入機制，讓每個用戶使用自己的 Google Sheet。

---

## 前置條件 ✅

- [x] Phase 4 完成
- [x] GCP 專案已設定 OAuth 2.0 憑證
- [x] 授權重新導向 URI 已設定

---

## 完成項目

### 5.1 GCP OAuth 設定 ✅

- [x] 建立 OAuth 2.0 憑證（Web Application 類型）
- [x] 設定授權重新導向 URI
  - 開發：`http://localhost:8000/api/auth/google/callback`
  - 生產：`https://your-domain/api/auth/google/callback`
- [x] 設定 OAuth 同意畫面
- [x] OAuth 授權範圍：
  - `openid` - OpenID Connect
  - `userinfo.email` - 用戶電子郵件
  - `userinfo.profile` - 用戶資訊
  - `spreadsheets` - Google Sheets 讀寫
  - `drive.readonly` - 列出 Google Drive 中的 Sheets

### 5.2 資料庫設定 ✅

- [x] 安裝依賴 (`aiosqlite`, `sqlalchemy[asyncio]`)
- [x] SQLite 資料庫結構（`backend/app/database/`）
  ```python
  # models.py
  class User(Base):
      id: str  # Google User ID
      email: str
      name: str
      picture: Optional[str]
      created_at: datetime

  class GoogleToken(Base):
      user_id: str (FK)
      access_token: str
      refresh_token: str
      expires_at: datetime

  class APIToken(Base):
      id: int
      token_hash: str
      user_id: str (FK)
      description: str
      created_at: datetime
      expires_at: Optional[datetime]
      last_used_at: Optional[datetime]
      is_active: bool

  class UserSheet(Base):
      user_id: str (FK)
      sheet_id: str
      sheet_url: str
      sheet_name: str
  ```

- [x] CRUD 操作函數（`backend/app/database/crud.py`）

### 5.3 OAuth 認證流程 ✅

- [x] `GET /api/auth/google/login`
  - 產生 OAuth URL（含 state 參數）
  - 重導向至 Google 登入

- [x] `GET /api/auth/google/callback`
  - 驗證 state 參數
  - 交換 Authorization Code 為 Token
  - 取得用戶資訊
  - 建立/更新用戶資料
  - 儲存 Google Token
  - 重導向至前端（帶 JWT Token）

- [x] `POST /api/auth/logout`
  - 清除本地 Token

- [x] `GET /api/auth/me`
  - 回傳當前登入用戶資訊

- [x] `GET /api/auth/status`
  - 檢查認證狀態

### 5.4 JWT Session 管理 ✅

- [x] 使用 JWT Token（適合 SPA）
- [x] 實作認證中介層
  ```python
  async def get_current_user(
      credentials: HTTPAuthorizationCredentials = Depends(security)
  ) -> dict:
      # 支援 JWT (OAuth) 或 API Token
  ```

- [x] 支援兩種認證方式
  - OAuth Session（網頁登入用戶）
  - API Token（Siri 捷徑）

### 5.5 用戶專屬 Sheet ✅

- [x] `UserSheetsService` 類別（`backend/app/services/user_sheets_service.py`）
  - 使用用戶的 OAuth Token 操作 Sheet
  - 處理 Token 刷新

- [x] Sheet 管理 API（`backend/app/api/sheets.py`）
  - `GET /api/sheets/list` - 列出 Google Drive 中的所有 Sheets
  - `POST /api/sheets/select` - 選擇現有 Sheet
  - `POST /api/sheets/create` - 建立新 Sheet
  - `GET /api/sheets/my-sheet` - 取得用戶的 Sheet 資訊

- [x] 月份分頁管理
  - 自動建立月份分頁（YYYY-MM 格式）
  - 每個月份獨立分頁，方便統計

### 5.6 前端 OAuth 整合 ✅

- [x] 登入按鈕（導向 `/api/auth/google/login`）
- [x] 處理 OAuth 回調（從 URL 取得 Token）
- [x] Token 儲存至 localStorage
- [x] 認證狀態管理
- [x] 登出功能
- [x] 條件渲染（未登入/已登入狀態）
- [x] Sheet 選擇介面
  - 列出 Google Drive 中的所有 Sheets
  - 選擇現有 Sheet 或建立新 Sheet

### 5.7 API Token 與 OAuth 整合 ✅

- [x] Token 產生需登入後才可操作
- [x] Token 綁定用戶 ID
- [x] Token 管理 API
  - `GET /api/auth/token/list` - 列出用戶的 Tokens
  - `DELETE /api/auth/token/{id}` - 撤銷 Token

- [x] 記帳 API 支援兩種認證
  - OAuth Session（網頁）→ 用戶的 Sheet
  - API Token（Siri）→ Token 綁定用戶的 Sheet

---

## 完成條件 ✅

- [x] 可使用 Google 帳號登入
- [x] 每個用戶有自己的 Sheet
- [x] 可從 Google Drive 選擇現有 Sheet
- [x] Google Token 正確儲存與刷新
- [x] Siri 捷徑可使用（透過 API Token）
- [x] 前端登入/登出功能正常
- [x] 月份分頁自動建立

---

## 環境變數

```bash
# Google OAuth 2.0
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# JWT
JWT_SECRET_KEY=random-secret-for-jwt
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# 資料庫
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
```

---

## 已建立檔案

```
backend/
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py     # 資料庫連線
│   │   ├── models.py       # SQLAlchemy 模型
│   │   └── crud.py         # CRUD 操作
│   ├── services/
│   │   ├── oauth_service.py       # OAuth 服務
│   │   └── user_sheets_service.py # 用戶 Sheet 服務
│   ├── api/
│   │   ├── auth.py         # OAuth API 端點
│   │   └── sheets.py       # Sheet 管理 API
│   └── utils/
│       └── auth.py         # 認證工具（JWT + API Token）

frontend/
├── src/
│   ├── pages/
│   │   └── SettingsPage.tsx  # 設定頁面（含 Sheet 選擇）
│   └── services/
│       └── api.ts            # API 呼叫（含 OAuth、Sheet API）
```

---

## 下一階段

→ [Phase 6：部署上線](./phase-6-deployment.md) 🔲 待開發
