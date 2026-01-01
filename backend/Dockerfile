FROM python:3.11-slim

WORKDIR /app

# 複製並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# Cloud Run 使用 PORT 環境變數
EXPOSE 8080

# 啟動應用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
