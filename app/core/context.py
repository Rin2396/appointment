from dataclasses import dataclass

import aio_pika
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.config import AppSettings
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.mq.publisher import EventPublisher


@dataclass
class AppContext:
    settings: AppSettings
    engine: AsyncEngine | None = None
    session_factory: async_sessionmaker[AsyncSession] | None = None
    redis: Redis | None = None
    cache: RedisCache | None = None
    rabbit_connection: aio_pika.RobustConnection | None = None
    publisher: EventPublisher | None = None

    async def check_db(self) -> None:
        if not self.engine:
            raise RuntimeError("DB engine not initialized")
        async with self.engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

    async def check_redis(self) -> None:
        if not self.redis:
            raise RuntimeError("Redis not initialized")
        await self.redis.ping()

    async def check_rabbit(self) -> None:
        if not self.rabbit_connection:
            raise RuntimeError("Rabbit connection not initialized")
        channel = await self.rabbit_connection.channel()
        await channel.close()


app_context: AppContext | None = None

