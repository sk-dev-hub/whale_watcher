# data/whale_providers/clankapp.py
from .base import WhaleProvider, WhaleTransaction
from typing import List
from config.settings import Settings
import requests
from datetime import datetime

class ClankAppProvider(WhaleProvider):
    def __init__(self):
        self.key = Settings.CLANKAPP_API_KEY

    def is_available(self) -> bool:
        return True  # ClankApp работает без ключа (ограниченно)

    def get_large_transfers(self, min_usd=1_000_000, limit=3) -> List[WhaleTransaction]:
        url = "https://api.clankapp.com/v2/explorer/tx"
        params = {
            "s_amount_usd": "desc",
            "size": limit,
            "min_value": min_usd,
            "symbol": "btc"
        }
        if self.key:
            params["api_key"] = self.key

        try:
            r = requests.get(url, params=params, timeout=8)
            if r.status_code != 200:
                return []
            txs = r.json().get("txs", [])[:limit]
            return [self._normalize(tx) for tx in txs if tx.get("amount_usd", 0) >= min_usd]
        except:
            return []

    def _normalize(self, tx) -> WhaleTransaction:
        owner_type = lambda x: "exchange" if any(w in x.lower() for w in ["binance", "coinbase"]) else "unknown"
        return WhaleTransaction(
            amount=tx.get("amount", 0),
            amount_usd=tx.get("amount_usd", 0),
            symbol=tx.get("symbol", "BTC").upper(),
            from_owner=tx.get("from_owner", "unknown"),
            from_type=owner_type(tx.get("from_owner", "")),
            to_owner=tx.get("to_owner", "unknown"),
            to_type=owner_type(tx.get("to_owner", "")),
            timestamp=tx.get("timestamp", datetime.now().timestamp())
        )