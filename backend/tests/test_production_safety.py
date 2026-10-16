from __future__ import annotations

import pytest

from app.config import get_settings


def test_production_settings_flag():
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_startup_blocks_production_bypass(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_DEV_BYPASS", "true")
    get_settings.cache_clear()
    from app.main import startup

    with pytest.raises(RuntimeError, match="AUTH_DEV_BYPASS"):
        await startup()
