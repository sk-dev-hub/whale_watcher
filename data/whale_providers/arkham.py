# data/whale_providers/arkham.py
from .base import WhaleProvider, WhaleTransaction
from typing import List
from config.settings import Settings
import requests
from datetime import datetime

class ArkhamProvider(WhaleProvider):
    def __init__(self):
        self.key = Settings.ARKHAM_API_KEY
        self.base_url = "https://platform.arkhamintelligence.com/api/v1"

    def is_available(self) -> bool:
        return bool(self.key)

    def get_large_transfers(self, min_usd=1_000_000, limit=3) -> List[WhaleTransaction]:
        if not self.is_available():
            return []

        headers = {"Authorization": f"Bearer {self.key}"}
        params = {
            "chain": "bitcoin",
            "min_value_usd": min_usd,
            "limit": limit,
            "sort": "timestamp desc"
        }
        try:
            r = requests.get(f"{self.base_url}/transactions", headers=headers, params=params, timeout=8)
            if r.status_code != 200:
                return []
            data = r.json().get("transactions", [])
            return [self._normalize(tx) for tx in data[:limit] if tx.get("amount_usd", 0) >= min_usd]
        except:
            return []

    def _normalize(self, tx) -> WhaleTransaction:
        return WhaleTransaction(
            amount=tx.get("amount", 0),
            amount_usd=tx.get("amount_usd", 0),
            symbol=tx.get("asset", "BTC").upper(),
            from_owner=tx.get("from_entity_name", "unknown"),
            from_type=tx.get("from_entity_label", "unknown").lower(),
            to_owner=tx.get("to_entity_name", "unknown"),
            to_type=tx.get("to_entity_label", "unknown").lower(),
            timestamp=tx.get("timestamp", datetime.now().timestamp())
        )