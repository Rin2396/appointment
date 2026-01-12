from fastapi import APIRouter, HTTPException, status

import app.core.context as app_ctx

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict:
    errors: dict[str, str] = {}
    try:
        assert app_ctx.app_context
        await app_ctx.app_context.check_db()
    except Exception as exc:  # pragma: no cover - health path
        errors["db"] = str(exc)
    try:
        assert app_ctx.app_context
        await app_ctx.app_context.check_redis()
    except Exception as exc:
        errors["redis"] = str(exc)
    try:
        assert app_ctx.app_context
        await app_ctx.app_context.check_rabbit()
    except Exception as exc:
        errors["rabbitmq"] = str(exc)
    if errors:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=errors)
    return {"status": "ok"}

