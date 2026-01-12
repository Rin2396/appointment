from typing import Protocol


class EventPublisher(Protocol):
    async def publish(self, routing_key: str, payload: dict, headers: dict | None = None) -> None: ...

