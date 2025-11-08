# exchanges/binance.py
import ccxt.async_support as ccxt
from .base import Exchange
from config.settings import Settings
from utils.logger import get_logger

log = get_logger()

class BinanceExchange(Exchange):
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': Settings.BINANCE_API_KEY,
            'secret': Settings.BINANCE_SECRET,
            'sandbox': True,  # ← ТЕСТОВЫЙ РЕЖИМ! Убери для реала
            'enableRateLimit': True,
        })

    async def get_balance(self):
        try:
            balance = await self.exchange.fetch_balance()
            log.info("Баланс получен с Binance")
            return {k: v['free'] for k, v in balance['total'].items() if v['free'] > 0}
        except Exception as e:
            log.error(f"Ошибка баланса Binance: {e}", exc_info=True)
            return {}

    async def create_order(self, symbol: str, side: str, amount: float):
        try:
            order = await self.exchange.create_market_order(
                symbol=symbol,  # e.g., 'BTC/USDT'
                side=side,      # 'buy' or 'sell'
                amount=amount
            )
            log.info(f"Ордер создан: {side} {amount} {symbol} → ID: {order['id']}")
            return order
        except Exception as e:
            log.error(f"Ошибка ордера Binance: {e}", exc_info=True)
            return None

    async def get_price(self, symbol: str):
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            log.debug(f"Цена {symbol}: ${price}")
            return price
        except Exception as e:
            log.error(f"Ошибка цены Binance: {e}")
            return None

    async def close(self):
        await self.exchange.close()