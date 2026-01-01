# GitHub Actions 自動部署設定

本文件說明如何設定 GitHub Actions 自動部署流程。

---

## 前置需求

1. GitHub 儲存庫
2. GCP 專案已建立
3. Vercel 帳號已連結專案

---

## 設定步驟

### 1. GCP Workload Identity Federation（推薦）

使用 Workload Identity Federation 讓 GitHub Actions 安全地存取 GCP，不需要儲存服務帳戶金鑰。

#### 1.1 建立服務帳戶

```bash
# 設定專案
PROJECT_ID="ai-accounting-482914"
gcloud config set project $PROJECT_ID

# 建立服務帳戶
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions"

# 授予必要權限
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

#### 1.2 建立 Workload Identity Pool

```bash
# 建立 Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
    --location="global" \
    --display-name="GitHub Actions Pool"

# 建立 Provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --attribute-condition="assertion.repository=='你的GitHub用戶名/ai_accounting'"
```

#### 1.3 綁定服務帳戶

```bash
# 取得 Workload Identity Pool ID
POOL_ID=$(gcloud iam workload-identity-pools describe "github-pool" \
    --location="global" \
    --format="value(name)")

# 綁定服務帳戶
gcloud iam service-accounts add-iam-policy-binding \
    "github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/你的GitHub用戶名/ai_accounting"
```

#### 1.4 取得 Provider 資源名稱

```bash
gcloud iam workload-identity-pools providers describe "github-provider" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --format="value(name)"
```

輸出格式類似：
```
projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

---

### 2. Vercel Token 設定

#### 2.1 取得 Vercel Token

1. 前往 https://vercel.com/account/tokens
2. 點擊「Create」建立新 Token
3. 名稱：`GitHub Actions`
4. Scope：選擇你的團隊或個人帳號
5. 複製產生的 Token

#### 2.2 取得 Vercel Project 和 Org ID

```bash
cd frontend

# 連結專案（如果還沒連結）
vercel link

# 查看 .vercel/project.json 取得 projectId 和 orgId
cat .vercel/project.json
```

輸出範例：
```json
{
  "projectId": "prj_xxxxxxxxxxxx",
  "orgId": "team_xxxxxxxxxxxx"
}
```

---

### 3. 設定 GitHub Secrets

前往 GitHub 儲存庫 → Settings → Secrets and variables → Actions

新增以下 Secrets：

| Secret 名稱 | 說明 | 範例值 |
|-------------|------|--------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload Identity Provider 資源名稱 | `projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT` | 服務帳戶 Email | `github-actions@ai-accounting-482914.iam.gserviceaccount.com` |
| `VERCEL_TOKEN` | Vercel API Token | `xxxxxxxx` |
| `VERCEL_ORG_ID` | Vercel 組織/團隊 ID | `team_xxxxxxxxxxxx` |
| `VERCEL_PROJECT_ID` | Vercel 專案 ID | `prj_xxxxxxxxxxxx` |

---

## 使用方式

### 自動部署

推送到 `main` 分支時會自動觸發部署：

```bash
git add .
git commit -m "Your changes"
git push origin main
```

### 手動部署

1. 前往 GitHub → Actions
2. 選擇「Deploy to Production」工作流程
3. 點擊「Run workflow」

---

## 部署流程

```
Push to main
    │
    ├─► deploy-backend (Cloud Run)
    │   1. Checkout code
    │   2. Authenticate to GCP (Workload Identity)
    │   3. Deploy to Cloud Run
    │   4. Health check
    │
    ├─► deploy-frontend (Vercel)
    │   1. Checkout code
    │   2. Setup Node.js
    │   3. Build project
    │   4. Deploy to Vercel
    │
    └─► notify
        Summary of deployment results
```

---

## 常見問題

### Q: 部署失敗怎麼辦？

1. 查看 GitHub Actions 日誌找出錯誤
2. 確認 Secrets 設定正確
3. 確認 GCP 權限足夠

### Q: 如何只部署後端或前端？

可以修改 workflow 檔案，加入路徑過濾：

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'  # 只有 backend 變更才觸發
```

### Q: 如何在 PR 時預覽？

可以新增 Preview 工作流程，在 PR 時部署到預覽環境。

---

## 相關連結

- [GitHub Actions 文件](https://docs.github.com/en/actions)
- [GCP Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [Vercel CLI](https://vercel.com/docs/cli)
