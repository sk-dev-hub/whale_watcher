# core/decision_engine.py
def make_final_decision(whale_signal: dict, news_signal: dict) -> str:
    """
    Комбинирует сигналы китов и новостей
    """
    whale_conf = whale_signal.get("confidence", 0.0)
    news_conf = news_signal.get("confidence", 0.0)

    # Сильный сигнал: оба > 0.7 и совпадают
    if (whale_conf > 0.7 and news_conf > 0.7 and
        whale_signal["signal"] == news_signal["sentiment"]):
        return f"STRONG {whale_signal['signal']}"

    # Средний сигнал: хотя бы один > 0.7
    if whale_conf > 0.7:
        return whale_signal["signal"]
    if news_conf > 0.7:
        return news_signal["sentiment"]

    # Слабый или конфликт
    return "HOLD"