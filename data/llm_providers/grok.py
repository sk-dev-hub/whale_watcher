# data/llm_providers/grok.py
from .base import LLMProvider
from config.settings import Settings
import requests

class GrokProvider(LLMProvider):
    def __init__(self):
        self.key = Settings.GROK_API_KEY

    def is_available(self) -> bool:
        return bool(self.key)

    def analyze_sentiment(self, text: str) -> dict:
        if not self.is_available():
            return {"sentiment": "neutral", "confidence": 0.0}

        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}"}
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": "Ты аналитик крипто-новостей. Ответь только: POSITIVE, NEGATIVE или NEUTRAL и уверенность (0.0-1.0)."},
                {"role": "user", "content": f"Новость: {text}"}
            ],
            "temperature": 0.1
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            if r.status_code != 200:
                return {"sentiment": "neutral", "confidence": 0.0}
            resp = r.json()["choices"][0]["message"]["content"].strip()
            sentiment, conf = resp.split() if len(resp.split()) == 2 else (resp, "0.5")
            return {"sentiment": sentiment.upper(), "confidence": float(conf)}
        except:
            return {"sentiment": "neutral", "confidence": 0.0}