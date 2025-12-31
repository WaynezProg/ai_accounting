"""OpenAI LLM 服務"""

import json
from datetime import datetime
from openai import OpenAI

from app.config import settings
from app.models.schemas import AccountingRecord


class OpenAIService:
    """OpenAI 服務類別"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def parse_accounting_text(self, text: str) -> AccountingRecord:
        """
        解析記帳文字，提取結構化資料

        Args:
            text: 使用者輸入的記帳文字，如 "中午吃排骨便當120元"

        Returns:
            AccountingRecord: 結構化的記帳記錄
        """
        current_time = datetime.now()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """你是我的記帳小助手，我會給你一串訊息，根據訊息幫我整理出以下資訊：
- "時間"：當下時間戳（格式：YYYY-MM-DD HH:MM）
- "名稱"：花費內容名稱
- "類別"：屬於哪一種類（飲食、交通、娛樂、購物、居住、醫療、教育、其他）
- "花費"：金額（數字）
- "幣別"：哪一種貨幣，若未提供默認為 TWD
- "支付方式"：支付方式（現金、信用卡、悠遊卡等），若未提供可為 null

請用 JSON 格式回答，不要包含其他說明文字。""",
                },
                {
                    "role": "user",
                    "content": f"current_time: {current_time}, user_content: {text}",
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=256,
        )

        # 解析回應
        content = response.choices[0].message.content
        data = json.loads(content)

        return AccountingRecord(**data)


# 單例模式
openai_service = OpenAIService()
