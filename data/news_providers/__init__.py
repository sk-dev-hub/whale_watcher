# data/news_providers/__init__.py
"""
Фабрика для получения новостей.
Пробует провайдеры: CryptoPanic → CoinGecko → RSS → Mock.
Логирование через utils.logger.
"""
from typing import List
from .base import NewsProvider, NewsItem
from .cryptopanic import CryptoPanicProvider
from .coingecko import CoinGeckoNewsProvider
from .rss import RSSProvider
from .mock import MockNewsProvider
from utils.logger import get_logger

# Логгер с именем модуля
log = get_logger()

# Порядок приоритета провайдеров
PROVIDERS = [
    CryptoPanicProvider,
    CoinGeckoNewsProvider,
    RSSProvider,
    MockNewsProvider  # Всегда в конце — fallback
]


def get_news_providers() -> List[NewsProvider]:
    """
    Возвращает список инстансов провайдеров новостей.
    """
    return [P() for P in PROVIDERS]


def get_news(limit: int = 5) -> List[NewsItem]:
    """
    Пробует получить новости от доступных провайдеров.
    Возвращает первые валидные новости или пустой список.
    """
    providers = get_news_providers()
    available = [p for p in providers if p.is_available()]

    if not available:
        log.warning("Все провайдеры новостей недоступны")
        return []

    for provider in available:
        try:
            news = provider.get_latest_news(limit)
            if news:
                source_name = provider.__class__.__name__.replace("Provider", "").replace("News", "")
                log.info(f"Новости получены от: {source_name}")
                return news
        except Exception as e:
            log.warning(f"Провайдер {provider.__class__.__name__} упал: {e}", exc_info=True)
            continue

    log.warning("Все провайдеры новостей вернули пустые данные")
    return []