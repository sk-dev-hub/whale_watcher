# utils/telegram.py
import asyncio
from telegram.ext import Application
from telegram.error import TelegramError
from config.settings import Settings
from utils.logger import get_logger

log = get_logger()

class TelegramNotifier:
    def __init__(self):
        self.app = None
        self.chat_id = Settings.TELEGRAM_CHAT_ID
        self.enabled = bool(Settings.TELEGRAM_BOT_TOKEN and self.chat_id)

        if self.enabled:
            # Создаём приложение — единственный способ получить Bot в v20+
            self.app = Application.builder().token(Settings.TELEGRAM_BOT_TOKEN).build()
            log.info("Telegram: инициализирован (v22.5+)")

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.enabled or not self.app:
            log.debug("Telegram отключён")
            return False

        try:
            # Используем app.bot (Bot доступен только так)
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            log.info("Сообщение отправлено в Telegram")
            return True
        except TelegramError as e:
            log.error(f"Ошибка Telegram: {e}", exc_info=True)
            return False
        except Exception as e:
            log.error(f"Неизвестная ошибка: {e}", exc_info=True)
            return False

    async def send_signal(self, signal, whale_tx=None, news_analysis=None):
        action = signal["action"]
        emoji = "BUY" if "BUY" in action else "SELL" if "SELL" in action else "HOLD"
        strength = "STRONG" if "STRONG" in action else ""

        lines = [
            f"<b>{emoji} {strength} {action}</b>",
            f"<b>Уверенность:</b> {signal['confidence']:.1%}",
            "",
        ]

        if whale_tx:
            lines.append(f"<b>Кит:</b> {whale_tx.amount:.0f} {whale_tx.symbol} → {whale_tx.to_owner}")
        if news_analysis and news_analysis['confidence'] > 0.3:
            lines.append(f"<b>Новости:</b> {news_analysis['sentiment']} ({news_analysis['confidence']:.0%})")

        if "order_id" in signal:
            lines.append(f"<b>Ордер:</b> {signal['order_id']}")

        lines += ["", f"<i>{signal['reason']}</i>"]

        message = "\n".join(lines)
        await self.send_message(message)

# Глобальный экземпляр
notifier = TelegramNotifier()