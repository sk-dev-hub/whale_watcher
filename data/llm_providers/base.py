# data/llm_providers/base.py
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def analyze_sentiment(self, text: str) -> dict:
        """Возвращает: {'sentiment': 'positive'/'negative'/'neutral', 'confidence': 0.0-1.0}"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass