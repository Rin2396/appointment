import asyncio
import json
import logging
import signal
import time
from typing import Any

from aio_pika import Message, RobustChannel, connect_robust

from app.core.config import AppSettings, get_settings
from app.core.logging import setup_logging
from app.infrastructure.notifications.telegram import TelegramNotifier

logger = logging.getLogger(__name__)

DEBUG_LOG_PATH = "/Users/vladislavargun/Documents/GitHub/Cursor/Appointment Hub/.cursor/debug.log"


#region agent log
def _debug_log(hypothesis_id: str, message: str, data: dict) -> None:
    payload = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": hypothesis_id,
        "location": "worker/main.py",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass
#endregion


class NotificationWorker:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.notifier = TelegramNotifier(settings.telegram)
        self.channel: RobustChannel | None = None
        self._connection = None

    async def start(self) -> None:
        attempt = 1
        connection = None
        while connection is None:
            try:
                connection = await connect_robust(self.settings.rabbit.url)
                _debug_log("H4", "worker_rabbit_connected", {"attempt": attempt})
            except Exception as exc:
                _debug_log("H4", "worker_rabbit_connect_failed", {"attempt": attempt, "error": str(exc)})
                await asyncio.sleep(min(5, attempt))
                attempt += 1
        self._connection = connection
        self.channel = await connection.channel()
        queue = await self.channel.declare_queue(self.settings.rabbit.notifications_queue, durable=True)
        logger.info("Worker started, waiting for messages")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self._handle_message(message)

    async def close(self) -> None:
        if self.channel:
            await self.channel.close()
        if self._connection:
            await self._connection.close()

    async def _handle_message(self, message: Message) -> None:
        attempt = int(message.headers.get("attempt", 1))
        event = message.headers.get("event", "unknown")
        payload: dict[str, Any] = json.loads(message.body.decode())
        text = self._render_message(event, payload)
        success = await self.notifier.send_message(text)
        if not success and attempt < self.settings.rabbit.max_retries and self.channel:
            headers = dict(message.headers)
            headers["attempt"] = attempt + 1
            await self.channel.default_exchange.publish(
                Message(body=message.body, headers=headers), routing_key=self.settings.rabbit.notifications_queue
            )
            logger.warning("Notification failed, rescheduled (attempt %s)", attempt + 1)

    @staticmethod
    def _render_message(event: str, payload: dict[str, Any]) -> str:
        if event == "appointment.created":
            return (
                f"Новая запись {payload.get('appointment_id')} на слот {payload.get('slot_id')} "
                f"к провайдеру {payload.get('provider_id')}"
            )
        if event == "appointment.cancelled":
            return f"Отмена записи {payload.get('appointment_id')} для слота {payload.get('slot_id')}"
        return f"Событие {event}: {payload}"


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    worker = NotificationWorker(settings=settings)
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler(*_: Any) -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass

    worker_task = asyncio.create_task(worker.start())
    await stop_event.wait()
    await worker.close()
    await worker_task


if __name__ == "__main__":
    asyncio.run(main())

