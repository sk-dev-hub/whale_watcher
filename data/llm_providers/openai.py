# data/llm_providers/openai.py
from .base import LLMProvider
from config.settings import Settings
import openai

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.key = Settings.OPENAI_API_KEY
        if self.key:
            openai.api_key = self.key

    def is_available(self) -> bool:
        return bool(self.key)

    def analyze_sentiment(self, text: str) -> dict:
        if not self.is_available():
            return {"sentiment": "neutral", "confidence": 0.0}

        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ответь только: POSITIVE, NEGATIVE или NEUTRAL и уверенность (0.0-1.0)."},
                    {"role": "user", "content": text}
                ],
                temperature=0.1
            )
            result = resp.choices[0].message.content.strip()
            sentiment, conf = result.split() if len(result.split()) == 2 else (result, "0.5")
            return {"sentiment": sentiment.upper(), "confidence": float(conf)}
        except:
            return {"sentiment": "neutral", "confidence": 0.0}