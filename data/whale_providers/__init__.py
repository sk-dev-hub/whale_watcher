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
from config.settings import Settings
from utils.logger import get_logger

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


def get_whale_transactions(min_usd: float = None, limit: int = 3) -> List[WhaleTransaction]:
    """
    Пробует получить крупные транзакции от доступных провайдеров.
    Фильтрует по настройкам из .env.
    """
    min_usd = min_usd or Settings.WHALE_MIN_USD
    chain = get_provider_chain()
    available = [p for p in chain if p.is_available()]

    if not available:
        log.warning("Все провайдеры китов недоступны")
        return []

    for provider in available:
        try:
            raw_txs = provider.get_large_transfers(min_usd, limit * 5)
            if not raw_txs:
                continue

            filtered_txs = []
            for tx in raw_txs:
                # Фильтр 1: Символ
                if tx.symbol not in Settings.WHALE_SYMBOLS:
                    continue

                # Фильтр 2: Сумма
                if tx.usd_value < Settings.WHALE_MIN_USD:
                    continue

                # Фильтр 3: Игнор unknown → unknown
                if Settings.WHALE_IGNORE_UNKNOWN and tx.from_type == "unknown" and tx.to_type == "unknown":
                    log.debug(f"Игнор: {tx.amount} {tx.symbol} (unknown → unknown)")
                    continue

                filtered_txs.append(tx)
                if len(filtered_txs) >= limit:
                    break

            if filtered_txs:
                log.info(f"Киты от: {provider.__class__.__name__} ({len(filtered_txs)} шт.)")
                return filtered_txs

        except Exception as e:
            log.warning(f"Провайдер {provider.__class__.__name__} упал: {e}", exc_info=True)
            continue

    log.warning("Нет подходящих китов после фильтрации")
    return []