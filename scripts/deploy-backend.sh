#!/bin/bash
# =========================
# Backend 部署腳本 (Cloud Run)
# =========================

set -e

# 設定變數
PROJECT_ID="ai-accounting-482914"
REGION="asia-east1"
SERVICE_NAME="ai-accounting-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AI Accounting Backend 部署${NC}"
echo -e "${GREEN}========================================${NC}"

# 切換到 backend 目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/../backend"

echo -e "${YELLOW}1. 設定 GCP 專案...${NC}"
gcloud config set project ${PROJECT_ID}

echo -e "${YELLOW}2. 建構 Docker 映像...${NC}"
docker build -t ${IMAGE_NAME} .

echo -e "${YELLOW}3. 推送映像至 Container Registry...${NC}"
docker push ${IMAGE_NAME}

echo -e "${YELLOW}4. 部署至 Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest,\
JWT_SECRET_KEY=JWT_SECRET_KEY:latest,\
GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest,\
GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest,\
TURSO_DATABASE_URL=TURSO_DATABASE_URL:latest,\
TURSO_AUTH_TOKEN=TURSO_AUTH_TOKEN:latest" \
    --set-env-vars "ENV=production,\
PORT=8080,\
GOOGLE_REDIRECT_URI=https://ai-accounting-api-51386650140.asia-east1.run.app/api/auth/google/callback,\
FRONTEND_URL=https://ai-accounting.vercel.app,\
CORS_ORIGINS=https://ai-accounting.vercel.app,https://ai-accounting-waynezprog.vercel.app"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"

# 取得服務 URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo -e "${GREEN}服務 URL: ${SERVICE_URL}${NC}"

# 健康檢查
echo -e "${YELLOW}執行健康檢查...${NC}"
sleep 5
curl -s "${SERVICE_URL}/api/health" | python3 -m json.tool

echo -e "${GREEN}完成!${NC}"
