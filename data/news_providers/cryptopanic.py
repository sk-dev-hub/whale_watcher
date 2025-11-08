# data/news_providers/cryptopanic.py
from .base import NewsProvider, NewsItem
from config.settings import Settings
import requests
from typing import List

class CryptoPanicProvider(NewsProvider):
    def __init__(self):
        self.key = Settings.CRYPTOPANIC_API_KEY

    def is_available(self) -> bool:
        return bool(self.key)

    def get_latest_news(self, limit=5) -> List[NewsItem]:
        if not self.is_available():
            return []

        url = "https://cryptopanic.com/api/v1/posts/"
        params = {
            "auth_token": self.key,
            "currencies": "BTC",
            "filter": "hot",
            "public": "true"
        }
        try:
            r = requests.get(url, params=params, timeout=8)
            if r.status_code != 200:
                return []
            data = r.json().get("results", [])[:limit]
            return [self._normalize(item) for item in data]
        except:
            return []

    def _normalize(self, item) -> NewsItem:
        return NewsItem(
            title=item.get("title", ""),
            content=item.get("description", "")[:500],
            url=item.get("url", ""),
            published_at=item.get("published_at", ""),
            source="CryptoPanic"
        )