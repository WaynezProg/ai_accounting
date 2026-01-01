#!/bin/bash
# =========================
# 本地開發啟動腳本
# =========================

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}/.."

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AI Accounting 開發環境${NC}"
echo -e "${GREEN}========================================${NC}"

# 複製開發環境設定
echo -e "${YELLOW}設定開發環境...${NC}"

# Backend
if [ -f "${PROJECT_DIR}/backend/.env.development" ]; then
    cp "${PROJECT_DIR}/backend/.env.development" "${PROJECT_DIR}/backend/.env"
    echo -e "${GREEN}Backend .env 已設定為開發模式${NC}"
fi

# Frontend - Vite 會自動讀取 .env.development
echo -e "${GREEN}Frontend 將使用 .env.development${NC}"

echo -e "${YELLOW}啟動後端...${NC}"
cd "${PROJECT_DIR}/backend"

# 啟動虛擬環境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 背景啟動後端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}後端已啟動 (PID: ${BACKEND_PID})${NC}"

echo -e "${YELLOW}啟動前端...${NC}"
cd "${PROJECT_DIR}/frontend"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}前端已啟動 (PID: ${FRONTEND_PID})${NC}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  開發環境已啟動${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "後端: http://localhost:8000"
echo -e "前端: http://localhost:5173"
echo -e "API 文件: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服務${NC}"

# 捕捉 Ctrl+C 並清理
cleanup() {
    echo -e "\n${YELLOW}停止服務...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}已停止所有服務${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 等待
wait
