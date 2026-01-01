#!/bin/bash
# =========================
# Frontend 部署腳本 (Vercel)
# =========================

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AI Accounting Frontend 部署${NC}"
echo -e "${GREEN}========================================${NC}"

# 切換到 frontend 目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/../frontend"

echo -e "${YELLOW}1. 安裝依賴...${NC}"
npm install

echo -e "${YELLOW}2. 建構生產版本...${NC}"
npm run build

echo -e "${YELLOW}3. 部署至 Vercel...${NC}"
# 使用 --prod 部署到生產環境
vercel --prod

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"
