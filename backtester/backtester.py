# backtester/backtester.py
import os
import glob
from pathlib import Path
from typing import List, Tuple
import ccxt
import pandas as pd
import matplotlib.pyplot as plt
from config.settings import Settings
from datetime import datetime, timedelta
from utils.logger import get_logger

log = get_logger()



# === УНИВЕРСАЛЬНЫЙ ПУТЬ К ПАПКЕ backtests ===
BASE_DIR = Path(__file__).resolve().parent.parent  # whale_watcher/
BACKTEST_DIR = BASE_DIR / "backtester/backtests"
BACKTEST_DIR.mkdir(exist_ok=True)

class Backtester:
    def __init__(self, symbol='BTC/USDT', timeframe='1h', days=60):
        self.symbol = symbol
        self.timeframe = timeframe
        self.days = days
        self.exchange = ccxt.binance()  # Публичный доступ
        self.initial_balance = 10000  # $10k
        self.balance = self.initial_balance
        self.trades = []

    def fetch_historical_data(self):
        """
        Загружает OHLCV с Binance via ccxt.
        """
        since = int((datetime.now() - timedelta(days=self.days)).timestamp() * 1000)
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, since=since)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        log.info(f"Загружено {len(df)} свечей для бэктеста")
        return df

    def run_backtest(self, df):
        """
        Симулирует стратегию: BUY/SELL по сигналу (имитируем твои киты+новости).
        """
        position = 0
        entry_price = 0

        for i in range(1, len(df)):
            price = df['close'].iloc[i]

            # Имитация сигнала: простой RSI (замени на твою логику)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            signal = 'BUY' if rsi.iloc[i] < 30 else 'SELL' if rsi.iloc[i] > 70 else 'HOLD'

            if signal == 'BUY' and position == 0:
                position = self.balance / price * 0.98  # 2% риск
                entry_price = price
                self.trades.append({'type': 'BUY', 'price': price, 'time': df.index[i]})
                log.debug(f"Бэктест BUY @ {price}")

            elif signal == 'SELL' and position > 0:
                self.balance = position * price * 0.98  # Комиссия 0.1%
                self.trades.append({'type': 'SELL', 'price': price, 'time': df.index[i]})
                log.debug(f"Бэктест SELL @ {price}")
                position = 0

        if position > 0:  # Закрыть позицию
            self.balance = position * df['close'].iloc[-1]

        profit_pct = (self.balance - self.initial_balance) / self.initial_balance * 100
        log.info(f"Бэктест завершён: Прибыль {profit_pct:.2f}% ({len(self.trades)} сделок)")
        return profit_pct, self.trades

    def plot_results(self, df, trades, profit_pct):
        from datetime import datetime

        # Имя файла
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        profit_str = f"{'+' if profit_pct >= 0 else ''}{profit_pct:.2f}".replace(".", ",")
        filename = BACKTEST_DIR / f"backtest_{timestamp}_profit_{profit_str}%.png"

        # График
        plt.figure(figsize=(14, 7))
        plt.plot(df.index, df['close'], label='BTC/USDT', color='blue', alpha=0.7)

        buys = [t for t in trades if t['type'] == 'BUY']
        sells = [t for t in trades if t['type'] == 'SELL']

        if buys:
            plt.scatter([t['time'] for t in buys], [t['price'] for t in buys],
                       color='green', marker='^', s=120, label='BUY', zorder=5)
        if sells:
            plt.scatter([t['time'] for t in sells], [t['price'] for t in sells],
                       color='red', marker='v', s=120, label='SELL', zorder=5)

        plt.title(f'Бэктест BTC/USDT | {self.days} дней | Прибыль: {profit_pct:+.2f}%')
        plt.xlabel('Время')
        plt.ylabel('Цена (USDT)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()

        log.info(f"График сохранён: {filename}")

        # УМНАЯ ОЧИСТКА
        Backtester.cleanup_backtests()

    @staticmethod
    def cleanup_backtests():
        """
        Умная очистка с настройками из .env
        """
        if not BACKTEST_DIR.exists():
            return

        files: List[Tuple[Path, float, float, datetime]] = []
        total_size_mb = 0

        for file_path in BACKTEST_DIR.glob("backtest_*.png"):
            try:
                name = file_path.stem
                profit_str = name.split("_profit_")[-1].replace(",", ".")
                profit = float(profit_str.rstrip("%"))
                size_mb = file_path.stat().st_size / (1024 * 1024)
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                files.append((file_path, profit, size_mb, mtime))
                total_size_mb += size_mb
            except Exception as e:
                log.warning(f"Пропущен файл {file_path.name}: {e}")
                continue

        if not files:
            return

        log.info(f"Очистка backtests: {len(files)} файлов, {total_size_mb:.1f} МБ")

        files.sort(key=lambda x: (-x[1], x[3]), reverse=True)

        max_size = Settings.BACKTEST_MAX_SIZE_MB
        max_files = Settings.BACKTEST_MAX_FILES
        max_age = Settings.BACKTEST_MAX_AGE_DAYS
        keep_profit = Settings.BACKTEST_KEEP_PROFIT_ABOVE

        to_keep = []
        current_size = 0
        current_count = 0

        for file_path, profit, size_mb, mtime in files:
            age_days = (datetime.now() - mtime).days

            if profit >= keep_profit or age_days <= 7:
                to_keep.append((file_path, size_mb))
                current_size += size_mb
                current_count += 1
                continue

            if (current_count >= max_files or
                current_size + size_mb > max_size or
                age_days > max_age):
                file_path.unlink()
                log.info(f"Удалён: {file_path.name} (+{profit:.2f}%, {age_days}д)")
            else:
                to_keep.append((file_path, size_mb))
                current_size += size_mb
                current_count += 1

        final_size = sum(s for _, s in to_keep)
        log.info(f"Осталось: {len(to_keep)} файлов, {final_size:.1f} МБ")


# Запуск бэктеста
if __name__ == "__main__":
    bt = Backtester()
    df = bt.fetch_historical_data()
    profit_pct, trades = bt.run_backtest(df)
    bt.plot_results(df, trades, profit_pct)