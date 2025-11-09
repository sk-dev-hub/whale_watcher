# core/analyzer.py
from config.settings import Settings
from data.whale_providers import WhaleTransaction
from utils.logger import get_logger

log = get_logger()

def analyze_whale(tx: WhaleTransaction) -> dict:
    signal = "HOLD"
    confidence = 0.5
    reason = "Анализ кита"

    # Пример: только биржи
    if tx.to_type == "exchange":
        signal = "SELL"
        confidence = 0.85
        reason = f"Перевод на биржу {tx.to_owner} — риск дампа"
    elif tx.from_type == "exchange":
        signal = "BUY"
        confidence = 0.80
        reason = f"Вывод с биржи {tx.from_owner} — накопление"

    # Доп. фильтр: игнорировать мелкие
    if tx.usd_value < Settings.WHALE_MIN_USD * 1.5:
        confidence *= 0.7
        reason += " (сумма ниже порога)"

    return {
        "signal": signal,
        "confidence": round(confidence, 2),
        "reason": reason
    }