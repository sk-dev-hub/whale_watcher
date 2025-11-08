# data/whale_providers/mock.py
from .base import WhaleProvider, WhaleTransaction
from datetime import datetime
from typing import List
import random

class MockProvider(WhaleProvider):
    def is_available(self) -> bool:
        return True

    def get_large_transfers(self, min_usd=1_000_000, limit=3) -> List[WhaleTransaction]:
        now = datetime.now().timestamp()
        return [
            WhaleTransaction(
                amount=1200 + random.randint(0, 500),
                amount_usd=75_000_000 + random.randint(0, 20_000_000),
                symbol="BTC",
                from_owner="Whale #42",
                from_type="whale",
                to_owner="Binance",
                to_type="exchange",
                timestamp=now - random.randint(60, 1800)
            )
        ]