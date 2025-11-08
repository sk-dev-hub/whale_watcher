# utils/telegram.py
import asyncio
import logging
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from config.settings import Settings
from utils.logger import get_logger

log = get_logger()


class TelegramNotifier:
    def __init__(self):
        self.bot = None
        self.chat_id = Settings.TELEGRAM_CHAT_ID
        self.enabled = bool(Settings.TELEGRAM_BOT_TOKEN and self.chat_id)

        if self.enabled:
            self.bot = Bot(token=Settings.TELEGRAM_BOT_TOKEN)
            log.info("Telegram-бот инициализирован")

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Отправляет сообщение в Telegram.
        Возвращает True если успешно.
        """
        if not self.enabled:
            log.debug("Telegram отключён в настройках")
            return False

        try:
            await self.bot.send_message(
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
            log.error(f"Неизвестная ошибка при отправке в Telegram: {e}", exc_info=True)
            return False

    async def send_signal(self, signal: dict, whale_tx=None, news_analysis=None):
        """
        Формирует и отправляет торговый сигнал.
        """
        emoji = "BUY" if "BUY" in signal["action"] else "SELL" if "SELL" in signal["action"] else "NEUTRAL"
        strength = "STRONG" if "STRONG" in signal["action"] else "Слабый"

        lines = [
            f"<b>{emoji} {strength} СИГНАЛ: {signal['action']}</b>",
            f"<b>Уверенность:</b> {signal.get('confidence', 0):.1%}",
            "",
            "<b>КИТЫ:</b>",
            f"• {whale_tx.amount} {whale_tx.symbol} → {whale_tx.to_owner} ({whale_tx.to_type})" if whale_tx else "• Нет активности",
            "",
            "<b>НОВОСТИ:</b>",
            f"• {news_analysis['sentiment']} ({news_analysis['confidence']:.0%}) — {news_analysis['source']}" if news_analysis else "• Нет данных",
            "",
            f"<i>{signal['reason']}</i>",
            "",
            f"⏰ {asyncio.get_event_loop().time():.0f}"
        ]

        message = "\n".join(lines)
        await self.send_message(message)


# Глобальный экземпляр
notifier = TelegramNotifier()