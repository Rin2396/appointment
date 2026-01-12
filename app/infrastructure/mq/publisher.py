import asyncio
import json

import aio_pika
from aio_pika import Message, RobustConnection

from app.application.interfaces.mq import EventPublisher as EventPublisherProtocol
from app.core.config import RabbitSettings

DEBUG_LOG_PATH = "/Users/vladislavargun/Documents/GitHub/Cursor/Appointment Hub/.cursor/debug.log"


#region agent log
def _debug_log(hypothesis_id: str, message: str, data: dict) -> None:
    payload = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": hypothesis_id,
        "location": "infrastructure/mq/publisher.py",
        "message": message,
        "data": data,
        "timestamp": int(asyncio.get_event_loop().time() * 1000),
    }
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass
#endregion


class EventPublisher(EventPublisherProtocol):
    def __init__(self, connection: RobustConnection, settings: RabbitSettings):
        self.connection = connection
        self.settings = settings

    async def publish(self, routing_key: str, payload: dict, headers: dict | None = None) -> None:
        target_routing = self.settings.notifications_queue or routing_key
        channel = await self.connection.channel()
        await channel.default_exchange.publish(
            Message(
                body=json.dumps(payload).encode(),
                headers=headers or {},
                content_type="application/json",
            ),
            routing_key=target_routing,
        )
        await channel.close()


async def create_rabbit_connection(url: str) -> RobustConnection:
    attempt = 1
    while True:
        try:
            conn = await aio_pika.connect_robust(url)
            _debug_log("H4", "rabbit_connected", {"attempt": attempt})
            return conn
        except Exception as exc:
            _debug_log("H4", "rabbit_connect_failed", {"attempt": attempt, "error": str(exc)})
            await asyncio.sleep(min(5, attempt))  # backoff but keep trying
            attempt += 1

