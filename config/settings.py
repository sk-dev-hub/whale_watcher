# config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    # === РЕЖИМ ===
    MODE = os.getenv("MODE", "TRADING").upper()

    # === ФЛАГИ ===
    ENABLE_TRADING = os.getenv("ENABLE_TRADING", "true").lower() == "true"
    ENABLE_BACKTEST = os.getenv("ENABLE_BACKTEST", "false").lower() == "true"

    # === TELEGRAM ===
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # @BotFather
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Твой ID или канал

    # === ФИЛЬТРЫ КИТОВ ===
    WHALE_SYMBOLS = [s.strip() for s in os.getenv("WHALE_SYMBOLS", "BTC").split(",")]
    WHALE_MIN_USD = float(os.getenv("WHALE_MIN_USD", "1000000"))
    WHALE_IGNORE_UNKNOWN = os.getenv("WHALE_IGNORE_UNKNOWN", "true").lower() == "true"

    # === БЭКТЕСТ ===
    BACKTEST_MAX_SIZE_MB = float(os.getenv("BACKTEST_MAX_SIZE_MB", "100"))
    BACKTEST_MAX_FILES = int(os.getenv("BACKTEST_MAX_FILES", "20"))
    BACKTEST_MAX_AGE_DAYS = int(os.getenv("BACKTEST_MAX_AGE_DAYS", "30"))
    BACKTEST_KEEP_PROFIT_ABOVE = float(os.getenv("BACKTEST_KEEP_PROFIT_ABOVE", "5.0"))

    ARKHAM_API_KEY = os.getenv("ARKHAM_API_KEY")
    CLANKAPP_API_KEY = os.getenv("CLANKAPP_API_KEY") # на будущее
    WHALE_ALERT_KEY = os.getenv("WHALE_ALERT_KEY")  # на будущее

    CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")

    GROK_API_KEY = os.getenv("GROK_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # === БИРЖИ ===
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET = os.getenv("BINANCE_SECRET")

    # === РИСК ===
    RISK_PER_TRADE = 0.02  # 2% от депозита
    MAX_POSITIONS = 3
    MIN_CONFIDENCE = 0.7