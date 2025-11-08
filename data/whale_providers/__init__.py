# data/whale_providers/__init__.py
"""
Фабрика для получения данных о китах.
Пробует провайдеры по очереди: Arkham → ClankApp → Mock.
Логирование через utils.logger.
"""
from typing import List
from .base import WhaleProvider, WhaleTransaction
from .arkham import ArkhamProvider
from .clankapp import ClankAppProvider
from .mock import MockProvider
from utils.logger import get_logger

# Логгер с именем модуля
log = get_logger()

# Порядок приоритета провайдеров
PROVIDERS = [
    ArkhamProvider,
    ClankAppProvider,
    MockProvider  # Всегда в конце — fallback
]


def get_provider_chain() -> List[WhaleProvider]:
    """
    Возвращает список инстансов провайдеров в порядке приоритета.
    """
    return [P() for P in PROVIDERS]


def get_whale_transactions(min_usd: float = 1_000_000, limit: int = 3) -> List[WhaleTransaction]:
    """
    Пробует получить крупные транзакции от доступных провайдеров.
    Возвращает первые валидные данные или пустой список.
    """
    chain = get_provider_chain()
    available = [p for p in chain if p.is_available()]

    if not available:
        log.warning("Все провайдеры недоступны")
        return []

    for provider in available:
        try:
            txs = provider.get_large_transfers(min_usd, limit)
            if txs:
                log.info(f"Данные получены от: {provider.__class__.__name__}")
                return txs
        except Exception as e:
            log.warning(f"Провайдер {provider.__class__.__name__} упал: {e}", exc_info=True)
            continue

    log.warning("Все провайдеры вернули пустые данные")
    return []