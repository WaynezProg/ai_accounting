# 變更記錄

本文件記錄專案的重要變更。

---

## [2026-01-01] 架構重構：移除 Service Account 模式

### 重大變更

#### 認證架構簡化
- **完全移除 Service Account 模式**：不再支援使用 Service Account 存取 Google Sheets
- **強制 OAuth 認證**：所有 Google Sheets 操作必須透過用戶的 OAuth 授權
- **Token 必須綁定用戶**：API Token 產生必須先登入，Token 會綁定到用戶帳號

#### 影響範圍
- Siri 捷徑用戶需要：
  1. 在網頁版使用 Google 帳號登入
  2. 建立或連結個人 Google Sheet
  3. 產生新的 API Token（舊的未綁定 Token 將無法使用）
  4. 更新 Siri 捷徑中的 Token

### 刪除的檔案
- `backend/app/services/google_sheets.py` - Service Account 服務

### 修改的檔案

#### 後端
- `backend/app/api/accounting.py` - 移除 fallback 到共用 Sheet 的邏輯
- `backend/app/api/auth.py` - Token 產生 API 必須登入才能使用
- `backend/app/config.py` - 移除 Service Account 相關設定
- `backend/.env.example` - 移除 Service Account 環境變數
- `backend/.env.development` - 移除 Service Account 環境變數
- `backend/.env.production` - 移除 Service Account 環境變數

#### 前端
- `frontend/src/hooks/useOpenAITTS.ts` - 新增 TTS 音訊快取機制
- `frontend/src/pages/HomePage.tsx` - TTS 改為手動播放（非自動播放）

#### 文件
- `README.md` - 更新環境變數說明、專案結構
- `docs/phases/README.md` - 更新功能說明

### 移除的環境變數
- `GOOGLE_SERVICE_ACCOUNT_FILE`
- `GOOGLE_SHEET_URL`
- `GOOGLE_SHEET_WORKSHEET`

### API 變更

| API | 變更 |
|-----|------|
| `POST /api/auth/token/generate` | 現在必須登入才能呼叫 |
| `POST /api/accounting/record` | 必須使用綁定用戶的 Token |
| `GET /api/accounting/stats` | 必須使用綁定用戶的 Token |
| `POST /api/accounting/query` | 必須使用綁定用戶的 Token |

### 錯誤訊息

未登入產生 Token：
```json
{
  "detail": "必須先登入才能產生 API Token。請先在網頁版使用 Google 帳號登入。"
}
```

使用未綁定用戶的 Token：
```json
{
  "detail": "此 API Token 未綁定用戶帳號。請先登入網頁版產生新的 Token。"
}
```

---

## [2025-12] TTS 功能優化

### 新增功能
- **TTS 音訊快取**：已播放過的語音會快取，「再聽一次」不需重新呼叫 API
- **手動播放模式**：理財回饋不再自動播放，由用戶點擊按鈕播放
- **快取狀態指示**：按鈕會顯示「聆聽」或「再聽一次」

### 修改的檔案
- `frontend/src/hooks/useOpenAITTS.ts`
- `frontend/src/pages/HomePage.tsx`

---

## [2025-12] Phase 6 完成：生產環境部署

### 部署架構
- **後端**：GCP Cloud Run (asia-east1)
- **前端**：Vercel
- **資料庫**：Turso libSQL
- **密鑰管理**：GCP Secret Manager

### 生產環境 URL
- 前端：https://frontend-omega-eight-30.vercel.app
- 後端：https://ai-accounting-api-51386650140.asia-east1.run.app
- API 文件：https://ai-accounting-api-51386650140.asia-east1.run.app/docs
