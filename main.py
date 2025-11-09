# main.py
import glob
import os
import asyncio
import schedule
import time
from datetime import datetime
from utils.logger import get_logger
from config.settings import Settings

# === ЛОГИРОВАНИЕ ===
log = get_logger()

# === РЕЖИМЫ ===
MODE = Settings.MODE
ENABLE_TRADING = Settings.ENABLE_TRADING
ENABLE_BACKTEST = Settings.ENABLE_BACKTEST

log.info(f"Запуск в режиме: {MODE}")
log.info(f"Торговля: {'ВКЛ' if ENABLE_TRADING else 'ВЫКЛ'}")
log.info(f"Бэктест: {'ВКЛ' if ENABLE_BACKTEST else 'ВЫКЛ'}")

# === ИМПОРТЫ ПО РЕЖИМУ ===
if MODE in ["TRADING", "SIGNALS_ONLY"]:
    from data.whale_tracker import get_whale_transactions
    from data.news_providers import get_news
    from core.analyzer import analyze_whale
    from core.news_analyzer import analyze_news_sentiment
    from core.decision_engine import make_final_decision
    from utils.telegram import notifier

    if ENABLE_TRADING:
        from exchanges.binance import BinanceExchange
        from exchanges.risk_manager import RiskManager
        exchange = BinanceExchange()
        risk_manager = RiskManager(exchange)

elif MODE == "BACKTEST":
    from backtester.backtester import Backtester
    log.info("Запуск бэктеста...")
    bt = Backtester(days=30)
    df = bt.fetch_historical_data()
    profit_pct, trades = bt.run_backtest(df)
    bt.plot_results(df, trades, profit_pct)
    log.info("Бэктест завершён. Выход.")
    exit(0)

# === ОСНОВНОЙ ЦИКЛ (ТОЛЬКО ДЛЯ TRADING / SIGNALS_ONLY) ===
async def check_market():
    log.info("=" * 70)
    log.info(f"АНАЛИЗ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 70)

    # 1. КИТЫ
    whale_txs = get_whale_transactions(min_usd=1_000_000, limit=1)
    whale_signal = {"signal": "HOLD", "confidence": 0.0, "reason": "Нет данных"}

    if whale_txs:
        tx = whale_txs[0]
        whale_signal = analyze_whale(tx)
        log.info(f"КИТ: {tx.amount:.2f} {tx.symbol} → {tx.to_owner}")
    else:
        log.warning("КИТЫ: Нет активности")

    # 2. НОВОСТИ + ИИ
    try:
        news_analysis = analyze_news_sentiment()
        log.info(f"НОВОСТИ: {news_analysis['sentiment']} ({news_analysis['confidence']:.0%})")
    except Exception as e:
        log.error(f"Ошибка новостей: {e}")
        news_analysis = {"sentiment": "NEUTRAL", "confidence": 0.0}

    # 3. ФИНАЛЬНОЕ РЕШЕНИЕ
    final_action = make_final_decision(whale_signal, news_analysis)
    log.info(f"СИГНАЛ: {final_action}")

    # 4. СИГНАЛ ДЛЯ TELEGRAM
    signal_data = {
        "action": final_action,
        "confidence": max(whale_signal["confidence"], news_analysis["confidence"]),
        "reason": whale_signal.get("reason", "Анализ рынка")
    }

    # 5. ТОРГОВЛЯ (ТОЛЬКО ЕСЛИ ВКЛЮЧЕНА)
    if ENABLE_TRADING and "STRONG" in final_action:
        if risk_manager.validate_signal(signal_data):
            side = "buy" if "BUY" in final_action else "sell"
            amount = await risk_manager.calculate_position_size("BTC/USDT")
            if amount > 0:
                order = await exchange.create_order("BTC/USDT", side, amount)
                if order:
                    signal_data["order_id"] = order.get("id", "—")
                    log.info(f"ОРДЕР: {side.upper()} {amount:.6f} BTC")
    else:
        log.info("Торговля отключена или слабый сигнал")

    # 6. ОТПРАВКА В TELEGRAM (ТОЛЬКО СИГНАЛ)
    try:
        await notifier.send_signal(
            signal=signal_data,
            whale_tx=whale_txs[0] if whale_txs else None,
            news_analysis=news_analysis
        )
    except Exception as e:
        log.error(f"Telegram: {e}")

    if ENABLE_TRADING:
        await exchange.close()

# === ОРКЕСТРАТОР ===
def job():
    if MODE in ["TRADING", "SIGNALS_ONLY"]:
        asyncio.run(check_market())

# === ЗАПУСК ===
if __name__ == "__main__":
    if MODE == "BACKTEST":
        pass  # Уже выполнено выше
    else:
        log.info("Запуск мониторинга. Ctrl+C для остановки.")
        job()  # Первый запуск
        schedule.every(30).minutes.do(job)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Остановлено пользователем")