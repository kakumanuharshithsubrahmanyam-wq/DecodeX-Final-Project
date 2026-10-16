from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.config import get_settings
from app.core.exceptions import AppError, app_error_handler

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("rtgs")

settings = get_settings()

app = FastAPI(title=settings.app_name, version=__version__, docs_url="/docs", openapi_url="/openapi.json")
app.add_exception_handler(AppError, app_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https://rtgs-portal(?:-[a-z0-9]+-harshith-debugs-projects)?\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup() -> None:
    cfg = get_settings()
    if cfg.app_env == "production" and cfg.auth_dev_bypass:
        raise RuntimeError("AUTH_DEV_BYPASS must be disabled when APP_ENV=production")
    if cfg.app_env == "production" and not cfg.supabase_jwt_secret and not cfg.resolved_jwks_url:
        logger.warning("Production JWT verification may be misconfigured (no secret/JWKS)")
    logger.info("Starting %s v%s env=%s", cfg.app_name, __version__, cfg.app_env)
