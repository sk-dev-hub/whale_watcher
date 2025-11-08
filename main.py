# main.py
import asyncio
import schedule
import time
from datetime import datetime
from utils.logger import get_logger
from data.whale_tracker import get_whale_transactions
from data.news_providers import get_news
from data.llm_providers import get_llm_chain
from core.analyzer import analyze_whale
from core.news_analyzer import analyze_news_sentiment
from core.decision_engine import make_final_decision
from exchanges.binance import BinanceExchange
from exchanges.risk_manager import RiskManager
from utils.telegram import notifier

# === ЛОГИРОВАНИЕ ===
log = get_logger()

# === ИНИЦИАЛИЗАЦИЯ ===
exchange = BinanceExchange()
risk_manager = RiskManager(exchange)

# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
SYMBOL = "BTC/USDT"
MIN_CONFIDENCE = 0.7


async def check_market():
    """
    Основной цикл анализа: киты + новости → сигнал → торговля + уведомления
    """
    log.info("=" * 70)
    log.info(f"АНАЛИЗ РЫНКА: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 70)

    # 1. КИТЫ
    whale_txs = get_whale_transactions(min_usd=1_000_000, limit=1)
    whale_signal = {"signal": "HOLD", "confidence": 0.0, "reason": "Нет данных о китах"}

    if whale_txs:
        tx = whale_txs[0]
        whale_signal = analyze_whale(tx)
        log.info(f"КИТ: {tx.amount:.2f} {tx.symbol} → {tx.to_owner} ({tx.to_type})")
        log.info(f"  → Сигнал: {whale_signal['signal']} | Уверенность: {whale_signal['confidence']:.2f}")
        log.info(f"  → Причина: {whale_signal['reason']}")
    else:
        log.warning("КИТЫ: Нет активности")

    # 2. НОВОСТИ + ИИ-АНАЛИЗ
    try:
        news_analysis = analyze_news_sentiment()
        log.info(f"НОВОСТИ: {news_analysis['sentiment']} | Уверенность: {news_analysis['confidence']:.2f}")
        log.info(f"  → Источник: {news_analysis['source']} | Новостей: {news_analysis['news_count']}")
    except Exception as e:
        log.error(f"Ошибка анализа новостей: {e}", exc_info=True)
        news_analysis = {"sentiment": "NEUTRAL", "confidence": 0.0, "source": "error"}

    # 3. ФИНАЛЬНОЕ РЕШЕНИЕ
    final_action = make_final_decision(whale_signal, news_analysis)
    log.info(f"ФИНАЛЬНОЕ РЕШЕНИЕ: {final_action}")

    # 4. ПОДГОТОВКА СИГНАЛА ДЛЯ ТОРГОВЛИ И УВЕДОМЛЕНИЙ
    signal_data = {
        "action": final_action,
        "confidence": max(whale_signal["confidence"], news_analysis["confidence"]),
        "reason": whale_signal.get("reason", "Комбинированный сигнал")
    }

    # 5. РИСК-МЕНЕДЖМЕНТ И ТОРГОВЛЯ
    if "STRONG" in final_action and risk_manager.validate_signal(signal_data):
        side = "buy" if "BUY" in final_action else "sell"
        try:
            amount = await risk_manager.calculate_position_size(SYMBOL)
            if amount > 0:
                log.info(f"Создание ордера: {side.upper()} {amount:.6f} {SYMBOL}")
                order = await exchange.create_order(SYMBOL, side, amount)
                if order:
                    signal_data["order_id"] = order.get("id", "unknown")
                    log.info(f"Ордер выполнен: {order['id']}")
                else:
                    log.error("Ордер не создан")
            else:
                log.warning("Размер позиции = 0 → торговля пропущена")
        except Exception as e:
            log.error(f"Ошибка торговли: {e}", exc_info=True)
    else:
        log.info("Торговля пропущена: слабый сигнал или риск")

    # 6. ОТПРАВКА В TELEGRAM
    try:
        await notifier.send_signal(
            signal=signal_data,
            whale_tx=whale_txs[0] if whale_txs else None,
            news_analysis=news_analysis
        )
    except Exception as e:
        log.error(f"Ошибка отправки в Telegram: {e}", exc_info=True)

    # 7. Закрытие соединения
    await exchange.close()
    log.info("=" * 70)


# === ОРКЕСТРАТОР ===
def job():
    """Запуск асинхронного анализа"""
    try:
        asyncio.run(check_market())
    except Exception as e:
        log.critical(f"Критическая ошибка в job(): {e}", exc_info=True)


# === ПЕРВЫЙ ЗАПУСК + ПЛАНИРОВЩИК ===
if __name__ == "__main__":
    log.info("WhaleWatcher AI запущен")
    log.info("Проверка каждые 30 минут. Ctrl+C для остановки.")

    # Первый запуск сразу
    job()

    # Планировщик
    schedule.every(30).minutes.do(job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Остановлено пользователем")
        log.info("До свидания!")