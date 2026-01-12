import logging

import httpx

from app.application.interfaces.notifier import Notifier
from app.core.config import TelegramSettings

logger = logging.getLogger(__name__)


class TelegramNotifier(Notifier):
    def __init__(self, settings: TelegramSettings):
        self.settings = settings

    async def send_message(self, text: str) -> bool:
        if not self.settings.bot_token or not self.settings.chat_id:
            logger.error("Telegram credentials missing; notification failed")
            return False
        url = f"https://api.telegram.org/bot{self.settings.bot_token}/sendMessage"
        payload = {"chat_id": self.settings.chat_id, "text": text}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error("Telegram API error %s: %s", response.status_code, response.text)
                return False
        return True

