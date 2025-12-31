# 語音記帳助手

整合 Siri 捷徑、LLM 和 Google Sheets 的智慧記帳系統。

## 功能特色

- 🎙️ **語音記帳**：透過 Siri 捷徑或網頁語音輸入記帳
- 🤖 **AI 智慧解析**：使用 GPT-4 自動解析記帳內容（日期、金額、類別）
- 📊 **Google Sheets 儲存**：記帳資料自動寫入 Google Sheets
- 💡 **理財回饋**：每次記帳後提供 AI 理財建議
- 🔐 **API Token 認證**：安全的 API 存取機制

---

## 開發進度

### ✅ 已完成

| Phase | 功能 | 說明 |
|-------|------|------|
| 0 | 專案結構 | FastAPI 後端架構、環境設定 |
| 1 | 後端核心 | 記帳 API、LLM 解析、Google Sheets、統計查詢、理財回饋 |
| 2 | Siri 整合 | API Token 認證、Siri 捷徑設定文件 |

### 🔲 待開發

| Phase | 功能 | 說明 |
|-------|------|------|
| 3 | 前端開發 | React + shadcn/ui 網頁介面、語音輸入/輸出 |
| 4 | 功能補強 | 統計圖表、進階查詢 |
| 5 | Google OAuth | 用戶登入、個人專屬 Sheet |
| 6 | 部署 | GCP 部署、CI/CD |

---

## 技術棧

### 後端
- **框架**：FastAPI (Python)
- **LLM**：OpenAI GPT-4 Turbo
- **資料儲存**：Google Sheets (Service Account)
- **認證**：Bearer Token

### 前端（規劃中）
- **框架**：React + TypeScript + Vite
- **UI**：shadcn/ui (Radix UI + Tailwind CSS)
- **語音**：Web Speech API

---

## 快速開始

### 前置需求

- Python 3.11+
- OpenAI API Key
- Google Cloud 專案 + Service Account

### 安裝

```bash
# 進入後端目錄
cd backend

# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 設定環境變數

```bash
# 複製範本
cp .env.example .env

# 編輯 .env 填入你的設定
```

**.env 必填項目：**

```bash
OPENAI_API_KEY=sk-xxx
GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/xxx
```

### 啟動服務

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

- API 文件：http://localhost:8000/docs
- 健康檢查：http://localhost:8000/health

---

## API 端點

| 方法 | 路徑 | 認證 | 說明 |
|------|------|:----:|------|
| GET | `/health` | ❌ | 健康檢查 |
| POST | `/api/auth/token/generate` | ❌ | 產生 API Token |
| GET | `/api/auth/token/verify` | ✅ | 驗證 Token |
| POST | `/api/accounting/record` | ✅ | 記帳 |
| GET | `/api/accounting/stats` | ✅ | 月度統計 |
| POST | `/api/accounting/query` | ✅ | 自然語言查詢 |
| GET | `/api/accounting/categories` | ❌ | 類別清單 |

> **認證說明：**
> - ✅ 需要在 Header 提供 `Authorization: Bearer <token>`
> - ❌ 不需要認證，原因如下：
>   - `/health`：供監控系統使用，需公開存取
>   - `/api/auth/token/generate`：產生 Token 的入口，否則無法取得第一個 Token
>   - `/api/accounting/categories`：類別清單為公開資訊，不涉及用戶資料
>
> **注意**：Phase 5 實作 Google OAuth 後，`/api/auth/token/generate` 將改為需要登入才能使用。

### 使用範例

**產生 Token：**
```bash
curl -X POST "http://localhost:8000/api/auth/token/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Siri 捷徑"}'
```

**記帳：**
```bash
curl -X POST "http://localhost:8000/api/accounting/record" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"text": "午餐吃滷肉飯 80 元"}'
```

**回應範例：**
```json
{
  "success": true,
  "record": {
    "時間": "2024-01-15 12:30",
    "名稱": "午餐滷肉飯",
    "類別": "飲食",
    "花費": 80.0,
    "幣別": "TWD",
    "支付方式": null
  },
  "message": "已記錄：午餐滷肉飯 80.0TWD",
  "feedback": "本月飲食類別已消費 3,500 元，建議適度控制飲食支出。"
}
```

---

## Siri 捷徑設定

詳細設定步驟請參考 [Siri 捷徑設定教學](docs/siri-shortcut-setup.md)。

**快速摘要：**
1. 產生 API Token
2. 在 iPhone「捷徑」App 建立新捷徑
3. 加入「聽寫文字」→「取得 URL 內容」→「朗讀文字」
4. 設定語音觸發：「嘿 Siri，記一筆帳」

---

## 專案結構

```
ai_accounting/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 環境設定
│   │   ├── api/
│   │   │   ├── health.py        # 健康檢查
│   │   │   ├── auth.py          # 認證 API
│   │   │   └── accounting.py    # 記帳 API
│   │   ├── services/
│   │   │   ├── openai_service.py
│   │   │   └── google_sheets.py
│   │   ├── models/
│   │   │   ├── schemas.py       # Pydantic 模型
│   │   │   └── token.py         # Token 管理
│   │   └── utils/
│   │       ├── auth.py          # 認證工具
│   │       ├── categories.py    # 類別定義
│   │       └── exceptions.py    # 自訂例外
│   ├── credentials/             # Service Account 憑證
│   ├── data/                    # Token 儲存
│   ├── requirements.txt
│   └── .env
├── docs/
│   ├── phases/                  # 開發階段文件
│   └── siri-shortcut-setup.md   # Siri 設定教學
└── README.md
```

---

## 開發文件

詳細的開發任務規劃請參考：

- [task.md](task.md) - 完整專案規劃
- [docs/phases/](docs/phases/) - 各階段開發文件
  - [Phase 0: 重構專案結構](docs/phases/phase-0-restructure.md)
  - [Phase 1: 後端核心功能](docs/phases/phase-1-backend-core.md)
  - [Phase 2: Siri 捷徑整合](docs/phases/phase-2-siri-integration.md)
  - [Phase 3: 前端開發](docs/phases/phase-3-frontend.md)
  - [Phase 4: 功能補強](docs/phases/phase-4-enhancements.md)
  - [Phase 5: Google OAuth](docs/phases/phase-5-oauth.md)
  - [Phase 6: 部署與文件](docs/phases/phase-6-deployment.md)

---

## 未來規劃

- [ ] 網頁版語音記帳介面
- [ ] 統計圖表視覺化
- [ ] Google OAuth 2.0 多用戶支援
- [ ] 預算設定與提醒
- [ ] 記帳歷史查詢與篩選
- [ ] 資料匯出（CSV/Excel）
- [ ] GCP 雲端部署

---

## License

MIT
