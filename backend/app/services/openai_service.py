"""OpenAI LLM 服務"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from openai import OpenAI, APIError, RateLimitError, APIConnectionError

from app.config import settings
from app.models.schemas import AccountingRecord, MonthlyStats

logger = logging.getLogger(__name__)


class OpenAIServiceError(Exception):
    """OpenAI 服務錯誤"""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class OpenAIService:
    """OpenAI 服務類別"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_retries = 3

    def _call_with_retry(self, messages: list, response_format: dict = None) -> str:
        """
        帶重試機制的 API 呼叫

        Args:
            messages: 訊息列表
            response_format: 回應格式

        Returns:
            str: API 回應內容
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 512,
                }
                if response_format:
                    kwargs["response_format"] = response_format

                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content

            except RateLimitError as e:
                logger.warning(f"Rate limit hit, attempt {attempt + 1}/{self.max_retries}")
                last_error = e
                if attempt < self.max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # 指數退避

            except APIConnectionError as e:
                logger.error(f"API connection error: {e}")
                last_error = e

            except APIError as e:
                logger.error(f"API error: {e}")
                raise OpenAIServiceError("API_ERROR", f"OpenAI API 錯誤：{str(e)}")

        raise OpenAIServiceError("RETRY_EXHAUSTED", f"重試次數已達上限：{str(last_error)}")

    async def parse_accounting_text(self, text: str) -> AccountingRecord:
        """
        解析記帳文字，提取結構化資料

        Args:
            text: 使用者輸入的記帳文字，如 "中午吃排骨便當120元"

        Returns:
            AccountingRecord: 結構化的記帳記錄

        Raises:
            OpenAIServiceError: 解析失敗時拋出
        """
        current_time = datetime.now()

        messages = [
            {
                "role": "system",
                "content": """
                    你是我的記帳小助手，我會給你一串訊息，根據訊息幫我整理出以下資訊：
                    - "時間"：當下時間戳（格式：YYYY-MM-DD HH:MM）
                    - "名稱"：花費內容名稱
                    - "類別"：屬於哪一種類（飲食、交通、娛樂、購物、居住、醫療、教育、其他）
                    - "花費"：金額（數字）
                    - "幣別"：哪一種貨幣，若未提供默認為 TWD
                    - "支付方式"：支付方式（現金、信用卡、悠遊卡等），若未提供可為 null

                    請用 JSON 格式回答，不要包含其他說明文字。
                """,
            },
            {
                "role": "user",
                "content": f"current_time: {current_time}, user_content: {text}",
            },
        ]

        try:
            content = self._call_with_retry(messages, {"type": "json_object"})
            data = json.loads(content)
            logger.info(f"Parsed accounting: {data}")
            return AccountingRecord(**data)

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise OpenAIServiceError("PARSE_ERROR", "無法解析 LLM 回應")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise OpenAIServiceError("UNKNOWN_ERROR", f"解析失敗：{str(e)}")

    async def generate_feedback(
        self, record: AccountingRecord, stats: Optional[MonthlyStats] = None
    ) -> str:
        """
        生成理財回饋建議

        Args:
            record: 剛記錄的消費
            stats: 月度統計資料（可選）

        Returns:
            str: 理財建議文字
        """
        stats_info = ""
        if stats:
            category_amount = stats.by_category.get(record.類別, 0)
            stats_info = f"""
本月統計：
- 總支出：{stats.total} 元
- {record.類別}類別已花費：{category_amount} 元
- 記錄筆數：{stats.record_count} 筆"""

        messages = [
            {
                "role": "system",
                "content": """
                    你是一個友善的理財小助手。根據用戶的消費記錄和統計資料，給出簡短的理財建議。
                    回覆要求：
                    - 簡短（1-2 句話）
                    - 友善且正面
                    - 如果有統計資料，可以提及消費佔比或趨勢
                    - 不要過度說教
                """,
            },
            {
                "role": "user",
                "content": f"""用戶剛記錄：{record.類別} - {record.名稱} {record.花費}{record.幣別}
{stats_info}

請給出簡短的理財回饋。""",
            },
        ]

        try:
            feedback = self._call_with_retry(messages)
            return feedback.strip()
        except Exception as e:
            logger.warning(f"Failed to generate feedback: {e}")
            return f"已記錄 {record.名稱} {record.花費}{record.幣別}"

    async def text_to_speech(
        self, text: str, voice: str = "nova", speed: float = 1.0
    ) -> bytes:
        """
        文字轉語音 (TTS)

        Args:
            text: 要轉換的文字
            voice: 聲音選擇 (alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse)
            speed: 語速 (0.25 到 4.0)

        Returns:
            bytes: MP3 音訊資料
        """
        try:
            # 使用 gpt-4o-mini-tts 模型，對多語言（包括中文）有更好的支援
            response = self.client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                input=text,
                speed=speed,
            )
            return response.content

        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise OpenAIServiceError("TTS_ERROR", f"語音合成失敗：{str(e)}")

    async def answer_query(self, query: str, stats: MonthlyStats) -> str:
        """
        回答帳務查詢

        Args:
            query: 用戶的問題
            stats: 統計資料

        Returns:
            str: 回答內容
        """
        messages = [
            {
                "role": "system",
                "content": """
                    你是一個友善的記帳助手。根據用戶的統計資料回答問題。
                    回覆要求：
                    - 使用自然語言
                    - 提供具體數字
                    - 可以給出簡短建議
                """,
            },
            {
                "role": "user",
                "content": f"""
                    用戶問題：{query}
                    統計資料：
                    - 月份：{stats.month}
                    - 總支出：{stats.total} 元
                    - 記錄筆數：{stats.record_count} 筆
                    - 各類別支出：{json.dumps(stats.by_category, ensure_ascii=False)}
                    請回答用戶的問題。
                """,
            },
        ]

        try:
            answer = self._call_with_retry(messages)
            return answer.strip()
        except Exception as e:
            logger.error(f"Failed to answer query: {e}")
            raise OpenAIServiceError("QUERY_ERROR", f"查詢失敗：{str(e)}")


# 單例模式
openai_service = OpenAIService()
