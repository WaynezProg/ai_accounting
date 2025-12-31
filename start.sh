#!/bin/bash

# =========================
# 語音記帳助手 - 啟動腳本
# =========================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 專案根目錄
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  語音記帳助手 - 啟動中...${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}錯誤: 找不到 Python3${NC}"
    exit 1
fi

# 進入後端目錄
cd "$BACKEND_DIR"

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}建立虛擬環境...${NC}"
    python3 -m venv venv
fi

# 啟動虛擬環境
echo -e "${YELLOW}啟動虛擬環境...${NC}"
source venv/bin/activate

# 檢查依賴
echo -e "${YELLOW}檢查依賴套件...${NC}"
pip install -r requirements.txt -q

# 檢查 .env
if [ ! -f ".env" ]; then
    echo -e "${RED}錯誤: 找不到 .env 檔案${NC}"
    echo -e "${YELLOW}請複製 .env.example 並填入設定：${NC}"
    echo "  cp .env.example .env"
    exit 1
fi

# 檢查必要環境變數
source .env
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}錯誤: OPENAI_API_KEY 未設定${NC}"
    exit 1
fi

if [ -z "$GOOGLE_SHEET_URL" ]; then
    echo -e "${RED}錯誤: GOOGLE_SHEET_URL 未設定${NC}"
    exit 1
fi

# 顯示設定
echo ""
echo -e "${GREEN}✓ 環境檢查通過${NC}"
echo ""
echo -e "${BLUE}設定資訊:${NC}"
echo "  - 環境: ${ENV:-development}"
echo "  - Port: ${PORT:-8000}"
echo "  - OpenAI Model: ${OPENAI_MODEL:-gpt-4-turbo}"
echo ""

# 啟動伺服器
echo -e "${GREEN}啟動伺服器...${NC}"
echo ""
echo -e "${BLUE}================================${NC}"
echo -e "  API 文件: ${GREEN}http://localhost:${PORT:-8000}/docs${NC}"
echo -e "  健康檢查: ${GREEN}http://localhost:${PORT:-8000}/health${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止伺服器${NC}"
echo ""

uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --reload
