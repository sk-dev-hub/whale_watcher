# core/analyzer.py
def analyze_whale(tx):  # tx — это WhaleTransaction (объект)
    amount_usd = tx.amount_usd
    to_type = tx.to_type
    from_type = tx.from_type
    to_owner = tx.to_owner.lower()

    # Arkham-специфика: institution → сильный сигнал
    if amount_usd > 5_000_000 and to_type == "exchange":
        confidence = 0.85 if "binance" in to_owner else 0.8
        return {
            "signal": "SELL",
            "confidence": confidence,
            "reason": f"Институциональный перевод на биржу ({tx.to_owner}) — риск дампа"
        }
    if amount_usd > 3_000_000 and from_type == "exchange" and to_type in ["whale", "institution"]:
        return {
            "signal": "BUY",
            "confidence": 0.8,
            "reason": f"Вывод с биржи к киту ({tx.to_owner}) — накопление"
        }
    return {
        "signal": "HOLD",
        "confidence": 0.5,
        "reason": "Нейтрально"
    }