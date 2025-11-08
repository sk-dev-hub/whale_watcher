# data/whale_providers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class WhaleTransaction:
    amount: float
    amount_usd: float
    symbol: str
    from_owner: str
    from_type: str
    to_owner: str
    to_type: str
    timestamp: float

class WhaleProvider(ABC):
    @abstractmethod
    def get_large_transfers(self, min_usd: float = 1_000_000, limit: int = 3) -> List[WhaleTransaction]:
        """Возвращает список крупных транзакций"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Проверка: API ключ есть и работает"""
        pass