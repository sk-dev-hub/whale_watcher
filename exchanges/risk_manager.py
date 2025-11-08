# exchanges/risk_manager.py
from config.settings import Settings
from utils.logger import get_logger

log = get_logger()

class RiskManager:
    def __init__(self, exchange):
        self.exchange = exchange
        self.risk_per_trade = Settings.RISK_PER_TRADE  # 2%

    async def calculate_position_size(self, symbol: str, stop_loss_pct: float = 0.02):
        """
        Рассчитывает размер позиции: 2% от баланса USDT.
        """
        balance = await self.exchange.get_balance()
        usdt_balance = balance.get('USDT', 0)
        risk_amount = usdt_balance * self.risk_per_trade

        price = await self.exchange.get_price(symbol)
        if not price:
            return 0

        position_size = risk_amount / (price * stop_loss_pct)
        position_size = min(position_size, usdt_balance / price * 0.1)  # Макс 10% баланса

        log.info(f"Размер позиции: {position_size:.4f} BTC (риск: ${risk_amount:.2f})")
        return position_size

    def validate_signal(self, signal: dict) -> bool:
        """
        Проверяет: уверенность > 70%, не больше 3 позиций.
        """
        if signal.get('confidence', 0) < Settings.MIN_CONFIDENCE:
            log.warning("Сигнал отклонён: низкая уверенность")
            return False
        # TODO: Проверить открытые позиции (ccxt.fetch_positions)
        return True