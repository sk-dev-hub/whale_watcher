# data/whale_providers/__init__.py
from typing import List
from .arkham import ArkhamProvider
from .clankapp import ClankAppProvider
from .mock import MockProvider
from .base import WhaleProvider, WhaleTransaction

# Порядок приоритета: Arkham → ClankApp → Mock
PROVIDERS = [
    ArkhamProvider,
    ClankAppProvider,
    MockProvider
]

def get_provider_chain() -> List[WhaleProvider]:
    return [P() for P in PROVIDERS]

def get_whale_transactions(min_usd=1_000_000, limit=3) -> List[WhaleTransaction]:
    """
    Пробует провайдеры по очереди, возвращает первые валидные данные
    """
    chain = get_provider_chain()
    available = [p for p in chain if p.is_available()]

    for provider in available:
        try:
            txs = provider.get_large_transfers(min_usd, limit)
            if txs:
                print(f"Данные от: {provider.__class__.__name__}")
                return txs
        except Exception as e:
            print(f"{provider.__class__.__name__} упал: {e}")
            continue

    print("Все провайдеры недоступны → возврат пустого списка")
    return []