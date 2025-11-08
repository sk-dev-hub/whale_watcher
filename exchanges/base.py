# exchanges/base.py
from abc import ABC, abstractmethod


class Exchange(ABC):
    @abstractmethod
    async def get_balance(self):
        pass

    @abstractmethod
    async def create_order(self, symbol, side, amount):
        pass

    @abstractmethod
    async def get_price(self, symbol):
        pass