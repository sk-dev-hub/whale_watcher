# backtester/backtester.py
import ccxt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from utils.logger import get_logger

log = get_logger()


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

    def plot_results(self, df, trades):
        """
        График цены + сделок.
        """
        plt.figure(figsize=(14, 7))
        plt.plot(df.index, df['close'], label='BTC/USDT', alpha=0.7, color='blue')

        # Разделяем BUY и SELL
        buys = [t for t in trades if t['type'] == 'BUY']
        sells = [t for t in trades if t['type'] == 'SELL']

        # BUY точки
        if buys:
            buy_times = [t['time'] for t in buys]
            buy_prices = [t['price'] for t in buys]
            plt.scatter(buy_times, buy_prices, color='green', marker='^', s=120, label='BUY', zorder=5)

        # SELL точки
        if sells:
            sell_times = [t['time'] for t in sells]
            sell_prices = [t['price'] for t in sells]
            plt.scatter(sell_times, sell_prices, color='red', marker='v', s=120, label='SELL', zorder=5)

        plt.title(f'Бэктест: {self.symbol} | {self.days} дней | Прибыль: {self.balance - self.initial_balance:.2f} USD')
        plt.xlabel('Время')
        plt.ylabel('Цена (USDT)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.savefig('backtest_results.png', dpi=150)
        plt.show()
        log.info("График сохранён: backtest_results.png")


# Запуск бэктеста
if __name__ == "__main__":
    bt = Backtester()
    df = bt.fetch_historical_data()
    profit, trades = bt.run_backtest(df)
    bt.plot_results(df, trades)