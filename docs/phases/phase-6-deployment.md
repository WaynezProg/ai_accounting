# Phase 6：部署上線 🔲 待開發

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
    - Cloud Run API
    - Cloud SQL API
    - Secret Manager API

- [ ] 設定 Cloud SQL（生產環境資料庫）
  - 建立 PostgreSQL 實例
  - 設定連線授權
  - 取得連線字串
  - 建立資料庫 Schema

### 6.2 後端部署

- [ ] 建立 Dockerfile
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  EXPOSE 8080
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
  ```

- [ ] 建立 `.dockerignore`
  ```
  venv/
  __pycache__/
  *.pyc
  .env
  .git/
  data/
  credentials/
  ```

- [ ] 設定環境變數（Secret Manager）
  - OPENAI_API_KEY
  - GOOGLE_CLIENT_ID
  - GOOGLE_CLIENT_SECRET
  - DATABASE_URL
  - JWT_SECRET_KEY

- [ ] 部署後端至 Cloud Run
  ```bash
  gcloud run deploy ai-accounting-backend \
    --source . \
    --region asia-east1 \
    --allow-unauthenticated \
    --set-secrets=OPENAI_API_KEY=openai-api-key:latest
  ```

### 6.3 前端部署

- [ ] 建置前端
  ```bash
  cd frontend
  npm run build
  ```

- [ ] 選擇部署方式
  - 選項 A：Firebase Hosting（推薦，整合 GCP）
  - 選項 B：Vercel（簡單快速）
  - 選項 C：Cloud Storage + CDN

- [ ] Firebase Hosting 設定
  ```bash
  npm install -g firebase-tools
  firebase login
  firebase init hosting
  firebase deploy
  ```

- [ ] 設定環境變數
  - VITE_API_BASE_URL（指向 Cloud Run URL）

### 6.4 域名與 SSL

- [ ] 設定自訂域名（可選）
  - Cloud Run 自訂域名
  - Firebase Hosting 自訂域名
- [ ] 確認 HTTPS 正常運作
- [ ] 更新 OAuth 重新導向 URI

### 6.5 CI/CD 設定

- [ ] 建立 `cloudbuild.yaml`
  ```yaml
  steps:
    # Build backend
    - name: 'gcr.io/cloud-builders/docker'
      args: ['build', '-t', 'gcr.io/$PROJECT_ID/backend', './backend']

    # Push to Container Registry
    - name: 'gcr.io/cloud-builders/docker'
      args: ['push', 'gcr.io/$PROJECT_ID/backend']

    # Deploy to Cloud Run
    - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
      args:
        - 'gcloud'
        - 'run'
        - 'deploy'
        - 'ai-accounting-backend'
        - '--image=gcr.io/$PROJECT_ID/backend'
        - '--region=asia-east1'
  ```

- [ ] 設定 Cloud Build 觸發條件
  - Push to main branch
  - Pull Request preview（可選）

- [ ] GitHub Actions（替代方案）
  ```yaml
  name: Deploy
  on:
    push:
      branches: [main]
  jobs:
    deploy:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: google-github-actions/setup-gcloud@v1
        - run: gcloud run deploy ...
  ```

### 6.6 監控與日誌

- [ ] 設定 Cloud Logging
  - 後端日誌自動收集
  - 設定日誌保留期限

- [ ] 設定錯誤警報
  - Error rate 監控
  - Email / Slack 通知

- [ ] 設定效能監控
  - 回應時間追蹤
  - API 使用量統計

### 6.7 文件完善

- [ ] 更新 `README.md`
  - 專案說明
  - 功能介紹
  - 技術棧
  - 快速開始
  - 環境變數說明

- [ ] 建立 `docs/setup.md`
  - 開發環境設定
  - 前置需求
  - 安裝步驟
  - 本地執行

- [ ] 建立 `docs/deployment.md`
  - GCP 設定步驟
  - 環境變數清單
  - 部署流程
  - 故障排除

- [ ] 更新 `docs/siri-shortcut-setup.md`
  - 使用生產環境 URL
  - 更新截圖（如需要）

---

## 完成條件

- [ ] 後端部署成功，API 可存取
- [ ] 前端部署成功，網頁可開啟
- [ ] OAuth 流程正常運作
- [ ] Siri 捷徑可連接生產環境
- [ ] CI/CD 自動部署正常
- [ ] 文件完整

---

## 部署檢查清單

- [ ] 環境變數已設定（Secret Manager）
- [ ] 資料庫連線正常
- [ ] OAuth 重新導向 URI 已更新
- [ ] CORS 設定正確（允許前端域名）
- [ ] HTTPS 正常運作
- [ ] 日誌可查看
- [ ] 錯誤處理正常
- [ ] API 回應時間合理（< 3s）

---

## 成本估算

| 服務 | 預估費用 | 說明 |
|------|---------|------|
| Cloud Run | ~$5-10/月 | 低流量場景 |
| Cloud SQL | ~$10/月 | 最小規格 |
| Firebase Hosting | 免費 | 小流量 |
| OpenAI API | 視用量 | ~$0.01/次記帳 |

---

## 上線後維護

- 定期檢查日誌
- 監控 API 使用量
- 注意 OpenAI API 成本
- 定期更新依賴套件
- 備份資料庫
- 安全性更新

---

## 專案完成！

恭喜！語音記帳助手已成功部署。

### 後續可擴充功能

- [ ] 預算設定與提醒
- [ ] 記帳歷史查詢與篩選
- [ ] 資料匯出（CSV/Excel）
- [ ] 多幣別支援
- [ ] 週期性支出追蹤
- [ ] 分享帳本功能
