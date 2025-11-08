# data/news_providers/mock.py
from .base import NewsProvider, NewsItem
from typing import List
import random
from datetime import datetime, timedelta

class MockNewsProvider(NewsProvider):
    def __init__(self):
        self.mock_news = [
            NewsItem(
                title="Bitcoin ETF inflows hit $1B in a single day",
                content="Institutional investors poured over $1 billion into spot Bitcoin ETFs on Thursday, marking the highest single-day inflow since launch.",
                url="https://example.com/news1",
                published_at=(datetime.now() - timedelta(minutes=30)).isoformat(),
                source="MockNews"
            ),
            NewsItem(
                title="Whale moves 5,000 BTC to Binance",
                content="A large holder transferred 5,000 BTC (~$300M) to Binance, sparking sell-off fears among traders.",
                url="https://example.com/news2",
                published_at=(datetime.now() - timedelta(minutes=15)).isoformat(),
                source="MockNews"
            ),
            NewsItem(
                title="SEC delays Ethereum ETF decision again",
                content="The U.S. SEC has postponed its decision on Ethereum spot ETFs until Q1 2026, citing regulatory concerns.",
                url="https://example.com/news3",
                published_at=(datetime.now() - timedelta(hours=2)).isoformat(),
                source="MockNews"
            ),
        ]

    def is_available(self) -> bool:
        return True  # Всегда работает

    def get_latest_news(self, limit=5) -> List[NewsItem]:
        # Перемешиваем и возвращаем
        shuffled = self.mock_news[:]
        random.shuffle(shuffled)
        return shuffled[:limit]