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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup() -> None:
    logger.info("Starting %s v%s env=%s", settings.app_name, __version__, settings.app_env)
