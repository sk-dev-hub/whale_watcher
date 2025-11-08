# data/llm_providers/local.py
from .base import LLMProvider
import random

class LocalLLMProvider(LLMProvider):
    def is_available(self) -> bool:
        return True

    def analyze_sentiment(self, text: str) -> dict:
        sentiments = ["POSITIVE", "NEGATIVE", "NEUTRAL"]
        return {
            "sentiment": random.choice(sentiments),
            "confidence": round(random.uniform(0.6, 0.9), 2)
        }