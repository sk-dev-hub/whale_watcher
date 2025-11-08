# data/whale_tracker.py
import requests
from config.settings import Settings


def get_whale_alert(min_value=1_000_000):
    if not Settings.WHALE_ALERT_KEY:
        return _mock()

    url = "https://api.whale-alert.io/v1/transactions"
    params = {
        "api_key": Settings.WHALE_ALERT_KEY,
        "min_value": min_value,
        "limit": 3
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json().get("transactions", [])
    except:
        return _mock()


def _mock():
    return [{
        "amount": 1500,
        "amount_usd": 90_000_000,
        "symbol": "btc",
        "from": {"owner_type": "unknown"},
        "to": {"owner": "binance", "owner_type": "exchange"},
        "timestamp": 1731076500
    }]