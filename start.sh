#!/bin/bash

# =========================
# 語音記帳助手 - 啟動腳本
# =========================
# 用法:
#   ./start.sh        # 預設開發模式
#   ./start.sh dev    # 開發模式
#   ./start.sh prod   # 生產模式 (本地測試生產設定)

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
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# 環境參數 (預設為 dev)
ENV_MODE="${1:-dev}"

# 清理函數 - 關閉所有子程序
cleanup() {
    echo ""
    echo -e "${YELLOW}正在關閉服務...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}服務已關閉${NC}"
    exit 0
}

# 捕獲 Ctrl+C
trap cleanup SIGINT SIGTERM

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  語音記帳助手 - 啟動中...${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# ========================
# 環境設定
# ========================

if [ "$ENV_MODE" = "prod" ] || [ "$ENV_MODE" = "production" ]; then
    ENV_MODE="production"
    ENV_FILE=".env.production"
    echo -e "${YELLOW}模式: 生產環境 (Production)${NC}"
else
    ENV_MODE="development"
    ENV_FILE=".env.development"
    echo -e "${GREEN}模式: 開發環境 (Development)${NC}"
fi

echo ""

# ========================
# 後端設定
# ========================

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
echo -e "${YELLOW}檢查後端依賴套件...${NC}"
pip install -r requirements.txt -q

# 複製環境設定檔
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" .env
    echo -e "${GREEN}✓ 已載入 $ENV_FILE${NC}"
elif [ -f ".env" ]; then
    echo -e "${YELLOW}警告: 找不到 $ENV_FILE，使用現有 .env${NC}"
else
    echo -e "${RED}錯誤: 找不到 .env 檔案${NC}"
    echo -e "${YELLOW}請複製 .env.example 並填入設定：${NC}"
    echo "  cp .env.example .env.development"
    exit 1
fi

# 檢查必要環境變數
source .env
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}錯誤: OPENAI_API_KEY 未設定${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 後端環境檢查通過${NC}"

# ========================
# 前端設定
# ========================

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}錯誤: 找不到 Node.js${NC}"
    exit 1
fi

# 檢查前端目錄
FRONTEND_ENABLED=false
if [ -d "$FRONTEND_DIR" ]; then
    cd "$FRONTEND_DIR"

    # 複製前端環境設定檔
    FRONTEND_ENV_FILE=".env.${ENV_MODE}"
    if [ -f "$FRONTEND_ENV_FILE" ]; then
        cp "$FRONTEND_ENV_FILE" .env
        echo -e "${GREEN}✓ 前端已載入 $FRONTEND_ENV_FILE${NC}"
    fi

    # 檢查 node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安裝前端依賴套件...${NC}"
        npm install
    fi

    echo -e "${GREEN}✓ 前端環境檢查通過${NC}"
    FRONTEND_ENABLED=true
else
    echo -e "${YELLOW}警告: 前端目錄不存在，僅啟動後端${NC}"
fi

# ========================
# 顯示設定資訊
# ========================

echo ""
echo -e "${BLUE}設定資訊:${NC}"
echo "  - 環境: $ENV_MODE"
echo "  - 後端 Port: ${PORT:-8000}"
if [ "$FRONTEND_ENABLED" = true ]; then
    echo "  - 前端 Port: 5173"
fi
echo ""

# ========================
# 啟動服務
# ========================

echo -e "${GREEN}啟動服務...${NC}"
echo ""

# 啟動後端 (背景執行)
cd "$BACKEND_DIR"
source venv/bin/activate

if [ "$ENV_MODE" = "production" ]; then
    # 生產模式：不使用 --reload
    uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} &
else
    # 開發模式：使用 --reload
    uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --reload &
fi
BACKEND_PID=$!

# 等待後端啟動
sleep 2

# 啟動前端 (背景執行)
if [ "$FRONTEND_ENABLED" = true ]; then
    cd "$FRONTEND_DIR"

    if [ "$ENV_MODE" = "production" ]; then
        # 生產模式：先 build 再 preview
        echo -e "${YELLOW}建置前端...${NC}"
        npm run build
        npm run preview &
    else
        # 開發模式
        npm run dev &
    fi
    FRONTEND_PID=$!
fi

# 等待前端啟動
sleep 2

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  服務已啟動 ($ENV_MODE)${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
if [ "$FRONTEND_ENABLED" = true ]; then
    if [ "$ENV_MODE" = "production" ]; then
        echo -e "  ${GREEN}前端:${NC}     http://localhost:4173"
    else
        echo -e "  ${GREEN}前端:${NC}     http://localhost:5173"
    fi
fi
echo -e "  ${GREEN}後端 API:${NC} http://localhost:${PORT:-8000}"
echo -e "  ${GREEN}API 文件:${NC} http://localhost:${PORT:-8000}/docs"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服務${NC}"
echo ""

# 等待子程序
wait
