# main.py
import asyncio
import schedule
import time

from utils.logger import get_logger
from data.whale_tracker import get_whale_transactions
from data.news_providers import get_news
from core.analyzer import analyze_whale
from core.news_analyzer import analyze_news_sentiment
from core.decision_engine import make_final_decision
from exchanges.mock import MockExchange
from utils.telegram import notifier

log = get_logger()

# Инициализация биржи
exchange = MockExchange()

async def check_market():
    log.info("="*60)
    log.info(f"АНАЛИЗ РЫНКА: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("="*60)

    # 1. КИТЫ
    whale_txs = get_whale_transactions(min_usd=1_000_000, limit=1)
    whale_signal = {"signal": "HOLD", "confidence": 0.0, "reason": "Нет данных"}

    if whale_txs:
        tx = whale_txs[0]
        whale_signal = analyze_whale(tx)
        log.info(f"КИТ: {tx.amount} {tx.symbol} → {tx.to_owner} ({tx.to_type})")
        log.info(f"  → Сигнал: {whale_signal['signal']} | Уверенность: {whale_signal['confidence']:.2f}")
        log.info(f"  → Причина: {whale_signal['reason']}")
    else:
        log.warning("КИТЫ: Нет активности")

    # 2. НОВОСТИ + ИИ
    try:
        news_analysis = analyze_news_sentiment()
        log.info(f"НОВОСТИ: {news_analysis['sentiment']} | Уверенность: {news_analysis['confidence']:.2f}")
        log.info(f"  → Источник: {news_analysis['source']} | Новостей: {news_analysis['news_count']}")
    except Exception as e:
        log.error(f"ОШИБКА НОВОСТЕЙ: {e}", exc_info=True)
        news_analysis = {"sentiment": "NEUTRAL", "confidence": 0.0}

    # 3. ФИНАЛЬНОЕ РЕШЕНИЕ
    final_action = make_final_decision(whale_signal, news_analysis)
    log.info(f"\nФИНАЛЬНОЕ РЕШЕНИЕ: {final_action}")

    # 4. === ОТПРАВКА В TELEGRAM ===
    signal_data = {
        "action": final_action,
        "confidence": max(whale_signal["confidence"], news_analysis["confidence"]),
        "reason": whale_signal.get("reason", "Комбинированный сигнал")
    }

    await notifier.send_signal(
        signal=signal_data,
        whale_tx=whale_txs[0] if whale_txs else None,
        news_analysis=news_analysis
    )

    # 5. ТОРГОВЛЯ
    if "STRONG" in final_action:
        side = "BUY" if "BUY" in final_action else "SELL"
        amount_btc = 0.01
        try:
            result = await exchange.create_order("BTC/USDT", side, amount_btc)
            log.info(f"ОРДЕР: {side} {amount_btc} BTC → {result}")
        except Exception as e:
            log.error(f"ОШИБКА ОРДЕРА: {e}", exc_info=True)
    else:
        log.info("Торговля пропущена (слабый сигнал)")

    log.info("="*60)

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