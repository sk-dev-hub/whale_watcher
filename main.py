# main.py
import asyncio
import schedule
import time
from core.decision_engine import make_decision
from exchanges.mock import MockExchange
from data.whale_tracker import get_whale_transactions
from core.analyzer import analyze_whale

exchange = MockExchange()


async def check_whales():
    print("\nПроверка китов...")
    txs = get_whale_transactions(min_usd=1_000_000, limit=1)

    if not txs:
        print("Нет данных от провайдеров.")
        return

    tx = txs[0]
    signal = analyze_whale(tx)
    decision = make_decision(signal)

    print(f"Сигнал: {signal['signal']} | Уверенность: {signal['confidence']}")
    print(f"Решение: {decision['action']} | {decision['reason']}")

    if decision['action'] in ['BUY', 'SELL']:
        await exchange.create_order("BTC/USDT", decision['action'], 0.01)


def job():
    asyncio.run(check_whales())


# Первый запуск
job()
schedule.every(30).minutes.do(job)

print("WhaleWatcher запущен (масштабируемый режим)")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Остановлено.")