# exchanges/mock.py
from .base import Exchange
import random


class MockExchange(Exchange):
    def __init__(self):
        self.balance = {"USDT": 10000}

    async def get_balance(self):
        return self.balance

    async def create_order(self, symbol, side, amount):
        price = 60000 + random.randint(-100, 100)
        print(f"[MOCK] {side} {amount} {symbol} @ ${price}")
        return {"id": "mock123", "status": "filled"}

    async def get_price(self, symbol):
        return 60000 + random.randint(-500, 500)