# data/llm_providers/mock.py
from .base import LLMProvider
import random

class MockLLMProvider(LLMProvider):
    def __init__(self):
        self.responses = {
            "Bitcoin ETF": ("POSITIVE", 0.92),
            "whale": ("NEGATIVE", 0.78),
            "SEC": ("NEGATIVE", 0.85),
            "inflows": ("POSITIVE", 0.88),
            "delay": ("NEGATIVE", 0.80),
            "default": ("NEUTRAL", 0.6)
        }

    def is_available(self) -> bool:
        return True

    def analyze_sentiment(self, text: str) -> dict:
        text_lower = text.lower()
        for keyword, (sentiment, conf) in self.responses.items():
            if keyword in text_lower and keyword != "default":
                return {"sentiment": sentiment, "confidence": conf + random.uniform(-0.05, 0.05)}
        return {
            "sentiment": self.responses["default"][0],
            "confidence": self.responses["default"][1] + random.uniform(-0.1, 0.1)
        }