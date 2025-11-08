# data/news_providers/coingecko.py
from .base import NewsProvider, NewsItem
import requests
from typing import List

class CoinGeckoNewsProvider(NewsProvider):
    def is_available(self) -> bool:
        return True  # Бесплатно, без ключа

    def get_latest_news(self, limit=5) -> List[NewsItem]:
        url = "https://api.coingecko.com/api/v3/news"
        try:
            r = requests.get(url, timeout=8)
            if r.status_code != 200:
                return []
            data = r.json().get("data", [])[:limit]
            return [self._normalize(item) for item in data]
        except:
            return []

    def _normalize(self, item) -> NewsItem:
        return NewsItem(
            title=item.get("title", ""),
            content=item.get("description", "")[:500],
            url=item.get("url", ""),
            published_at=item.get("updated_at", ""),
            source="CoinGecko"
        )