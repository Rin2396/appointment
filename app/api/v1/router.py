from fastapi import APIRouter

from app.api.v1.routes import appointments, schedules, services, users

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])

