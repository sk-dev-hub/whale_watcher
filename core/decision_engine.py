# core/decision_engine.py
from config.settings import Settings


def make_decision(whale_signal, news_sentiment=None, price_trend=None):
    confidence = whale_signal["confidence"]

    if confidence < Settings.MIN_CONFIDENCE:
        return {"action": "HOLD", "reason": "Низкая уверенность"}

    return {
        "action": whale_signal["signal"],
        "amount_usd": 1000,  # потом будет риск-менеджер
        "reason": whale_signal["reason"]
    }