# config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    WHALE_ALERT_KEY = os.getenv("WHALE_ALERT_KEY")
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET = os.getenv("BINANCE_SECRET")

    RISK_PER_TRADE = 0.02  # 2% от депозита
    MAX_POSITIONS = 3
    MIN_CONFIDENCE = 0.7