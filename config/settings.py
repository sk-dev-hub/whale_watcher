# config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    ARKHAM_API_KEY = os.getenv("ARKHAM_API_KEY")
    CLANKAPP_API_KEY = os.getenv("CLANKAPP_API_KEY") # на будущее
    WHALE_ALERT_KEY = os.getenv("WHALE_ALERT_KEY")  # на будущее


    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET = os.getenv("BINANCE_SECRET")

    RISK_PER_TRADE = 0.02  # 2% от депозита
    MAX_POSITIONS = 3
    MIN_CONFIDENCE = 0.7