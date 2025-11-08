# data/news_providers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class NewsItem:
    title: str
    content: str
    url: str
    published_at: str
    source: str

class NewsProvider(ABC):
    @abstractmethod
    def get_latest_news(self, limit: int = 5) -> List[NewsItem]:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass