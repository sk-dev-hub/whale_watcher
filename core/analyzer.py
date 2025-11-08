# core/analyzer.py
def analyze_whale(tx):
    amount_usd = tx["amount_usd"]
    to_exchange = "exchange" in tx["to"].get("owner_type", "")
    from_exchange = "exchange" in tx["from"].get("owner_type", "")

    if amount_usd > 5_000_000 and to_exchange:
        return {"signal": "SELL", "confidence": 0.8, "reason": "Крупный перевод на биржу"}
    if amount_usd > 3_000_000 and not from_exchange:
        return {"signal": "BUY", "confidence": 0.75, "reason": "Накопление"}
    return {"signal": "HOLD", "confidence": 0.5, "reason": "Нейтрально"}