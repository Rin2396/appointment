import logging

from fastapi import FastAPI
from redis.asyncio import Redis

from app.api.v1.router import api_router
from app.api.v1.routes import health
from app.core import context
from app.core.config import get_settings
from app.core.db import create_engine, create_session_factory
from app.core.logging import setup_logging
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.mq.publisher import EventPublisher, create_rabbit_connection

logger = logging.getLogger(__name__)


settings = get_settings()
setup_logging(settings.log_level)
app = FastAPI(title=settings.app_name, openapi_url=f"{settings.api_prefix}/openapi.json")
app_context = context.AppContext(settings=settings)
context.app_context = app_context


@app.on_event("startup")
async def on_startup() -> None:
    app_context.engine = create_engine(settings.db.url)
    app_context.session_factory = create_session_factory(app_context.engine)
    app_context.redis = Redis.from_url(settings.redis.url, decode_responses=False)
    app_context.cache = RedisCache(app_context.redis, settings.redis)
    app_context.rabbit_connection = await create_rabbit_connection(settings.rabbit.url)
    app_context.publisher = EventPublisher(app_context.rabbit_connection, settings.rabbit)
    logger.info("Application started")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    if app_context.redis:
        await app_context.redis.close()
    if app_context.rabbit_connection:
        await app_context.rabbit_connection.close()
    if app_context.engine:
        await app_context.engine.dispose()
    logger.info("Application shutdown complete")


app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(health.router, tags=["health"])


def start() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    start()

