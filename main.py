# main.py
import asyncio
import schedule
import time
from data.whale_tracker import get_whale_transactions
from data.news_providers import get_news
from core.analyzer import analyze_whale
from core.news_analyzer import analyze_news_sentiment
from core.decision_engine import make_final_decision
from exchanges.mock import MockExchange

# Инициализация биржи
exchange = MockExchange()

async def check_market():
    print("\n" + "="*60)
    print(f"АНАЛИЗ РЫНКА: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # 1. КИТЫ
    whale_txs = get_whale_transactions(min_usd=1_000_000, limit=1)
    whale_signal = {"signal": "HOLD", "confidence": 0.0, "reason": "Нет данных"}

    if whale_txs:
        tx = whale_txs[0]
        whale_signal = analyze_whale(tx)
        print(f"КИТ: {tx.amount} {tx.symbol} → {tx.to_owner} ({tx.to_type})")
        print(f"  → Сигнал: {whale_signal['signal']} | Уверенность: {whale_signal['confidence']:.2f}")
        print(f"  → Причина: {whale_signal['reason']}")
    else:
        print("КИТЫ: Нет активности")

    # 2. НОВОСТИ + ИИ
    news_analysis = analyze_news_sentiment()
    print(f"НОВОСТИ: {news_analysis['sentiment']} | Уверенность: {news_analysis['confidence']:.2f}")
    print(f"  → Источник: {news_analysis['source']} | Новостей: {news_analysis['news_count']}")

    # 3. ФИНАЛЬНОЕ РЕШЕНИЕ
    final_action = make_final_decision(whale_signal, news_analysis)
    print(f"\nФИНАЛЬНОЕ РЕШЕНИЕ: {final_action}")

    # 4. ТОРГОВЛЯ (только если STRONG)
    if "STRONG" in final_action:
        side = "BUY" if "BUY" in final_action else "SELL"
        amount_btc = 0.01  # потом будет риск-менеджер
        result = await exchange.create_order("BTC/USDT", side, amount_btc)
        print(f"ОРДЕР: {side} {amount_btc} BTC → {result}")

    print("="*60)

# === ОРКЕСТРАТОР ===
def job():
    asyncio.run(check_market())

# Первый запуск сразу
job()

# Запуск каждые 1 минут
schedule.every(1).minutes.do(job)

print("WhaleWatcher AI запущен. Проверка каждые 1 минут.")
print("Для остановки: Ctrl+C")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nОстановлено пользователем.")