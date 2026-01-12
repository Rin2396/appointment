from collections.abc import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.context as app_ctx
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.mq.publisher import EventPublisher


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    assert app_ctx.app_context and app_ctx.app_context.session_factory
    async with app_ctx.app_context.session_factory() as session:
        yield session


async def get_cache() -> RedisCache:
    assert app_ctx.app_context and app_ctx.app_context.cache
    return app_ctx.app_context.cache


async def get_redis() -> Redis:
    assert app_ctx.app_context and app_ctx.app_context.redis
    return app_ctx.app_context.redis


async def get_publisher() -> EventPublisher:
    assert app_ctx.app_context and app_ctx.app_context.publisher
    return app_ctx.app_context.publisher

