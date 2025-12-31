# Phase 6：部署與文件

## 目標

將應用部署至 GCP，並完成所有文件。

---

## 前置條件

- [ ] Phase 5 完成
- [ ] 所有功能在本地測試通過
- [ ] GCP 專案已設定

---

## 任務清單

### 6.1 GCP 環境準備

- [ ] 確認 GCP 專案設定
  - Billing 已啟用
  - 必要 API 已啟用
    - Google Sheets API
    - Cloud Run API（或 App Engine）
    - Cloud SQL API（如使用）

- [ ] 設定 Cloud SQL（生產環境資料庫）
  - 建立 PostgreSQL 實例
  - 設定連線授權
  - 取得連線字串

### 6.2 後端部署

- [ ] 建立 Dockerfile
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
  ```

- [ ] 設定 Cloud Run
  ```yaml
  # deploy/gcp/cloudrun.yaml
  service: ai-accounting-backend
  runtime: python311
  env_variables:
    ENV: production
  ```

- [ ] 設定環境變數（Secret Manager）
  - OPENAI_API_KEY
  - GOOGLE_CLIENT_ID
  - GOOGLE_CLIENT_SECRET
  - DATABASE_URL
  - SECRET_KEY

- [ ] 部署後端
  ```bash
  gcloud run deploy ai-accounting-backend \
    --source . \
    --region asia-east1
  ```

### 6.3 前端部署

- [ ] 建置前端
  ```bash
  npm run build
  ```

- [ ] 選擇部署方式
  - 選項 A：Cloud Storage + CDN
  - 選項 B：Firebase Hosting
  - 選項 C：Vercel / Netlify

- [ ] 設定環境變數
  - VITE_API_BASE_URL（指向後端 URL）

- [ ] 部署前端

### 6.4 域名與 SSL

- [ ] 設定自訂域名（可選）
- [ ] 確認 HTTPS 正常運作
- [ ] 更新 OAuth 重新導向 URI

### 6.5 CI/CD 設定

- [ ] 建立 `cloudbuild.yaml`
  ```yaml
  steps:
    - name: 'gcr.io/cloud-builders/docker'
      args: ['build', '-t', 'gcr.io/$PROJECT_ID/backend', './backend']
    - name: 'gcr.io/cloud-builders/docker'
      args: ['push', 'gcr.io/$PROJECT_ID/backend']
    - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
      args: ['gcloud', 'run', 'deploy', ...]
  ```

- [ ] 設定觸發條件
  - Push to main branch
  - Pull Request preview（可選）

### 6.6 監控與日誌

- [ ] 設定 Cloud Logging
- [ ] 設定錯誤警報（可選）
- [ ] 設定效能監控（可選）

### 6.7 文件撰寫

- [ ] `README.md` - 專案總覽
  - 功能介紹
  - 技術棧
  - 快速開始
  - 環境變數說明

- [ ] `docs/setup.md` - 開發環境設定
  - 前置需求
  - 安裝步驟
  - 本地執行

- [ ] `docs/api.md` - API 文件
  - 或使用 FastAPI 自動生成的 `/docs`

- [ ] `docs/siri-shortcut-setup.md` - Siri 捷徑設定
  - 詳細步驟
  - 截圖說明
  - 常見問題

- [ ] `docs/deployment.md` - 部署文件
  - GCP 設定步驟
  - 環境變數清單
  - 故障排除

---

## 完成條件

- [ ] 後端部署成功，API 可存取
- [ ] 前端部署成功，網頁可開啟
- [ ] OAuth 流程正常運作
- [ ] Siri 捷徑可連接生產環境
- [ ] 文件完整

---

## 部署檢查清單

- [ ] 環境變數已設定
- [ ] 資料庫連線正常
- [ ] OAuth 重新導向 URI 已更新
- [ ] CORS 設定正確
- [ ] HTTPS 正常運作
- [ ] 日誌可查看
- [ ] 錯誤處理正常

---

## 上線後維護

- 定期檢查日誌
- 監控 API 使用量
- 注意 OpenAI API 成本
- 定期更新依賴套件

---

## 專案完成！

恭喜！語音記帳助手已成功部署。

後續可參考 task.md 的「後續擴充功能」章節繼續開發。
