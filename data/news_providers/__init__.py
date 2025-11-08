# data/news_providers/__init__.py
from typing import List
from .base import NewsProvider, NewsItem
from .cryptopanic import CryptoPanicProvider
from .coingecko import CoinGeckoNewsProvider
from .rss import RSSProvider
from .mock import MockNewsProvider

PROVIDERS = [
    CryptoPanicProvider,
    CoinGeckoNewsProvider,
    RSSProvider,
    MockNewsProvider
]

def get_news(limit=5) -> List[NewsItem]:
    for P in PROVIDERS:
        p = P()
        if p.is_available():
            try:
                news = p.get_latest_news(limit)
                if news:
                    source = p.__class__.__name__.replace("Provider", "")
                    print(f"Новости от: {source}")
                    return news
            except Exception as e:
                print(f"{p.__class__.__name__} упал: {e}")
                continue
    print("Все провайдеры новостей недоступны")
    return []