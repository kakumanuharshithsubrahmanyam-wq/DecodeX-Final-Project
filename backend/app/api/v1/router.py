from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import analytics, categories, dept, departments, grievances, health, me, notifications

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(me.router, tags=["profile"])
api_router.include_router(categories.router, tags=["categories"])
api_router.include_router(grievances.router, tags=["grievances"])
api_router.include_router(dept.router, tags=["department"])
api_router.include_router(departments.router, tags=["departments"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(analytics.router, tags=["analytics"])
