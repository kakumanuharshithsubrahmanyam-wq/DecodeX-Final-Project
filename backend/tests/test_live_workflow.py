"""
Live RTGS workflow tests — require RTGS_LIVE_TEST=1 and backend/.env pointing at rtgs-dev.
Never run against TEAM-DDMM, printkiosk, or production.
"""
from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RTGS_LIVE_TEST") != "1",
    reason="Set RTGS_LIVE_TEST=1 and configure backend/.env for rtgs-dev",
)


@pytest.mark.asyncio
async def test_live_health_database():
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["data"]["database"] == "ok"


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_grievance_with_real_jwt():
    """Requires RTGS_LIVE_TEST_USER_EMAIL, RTGS_LIVE_TEST_PASSWORD, and Supabase Auth."""
    email = os.getenv("RTGS_LIVE_TEST_USER_EMAIL")
    password = os.getenv("RTGS_LIVE_TEST_PASSWORD")
    if not email or not password:
        pytest.skip("Set RTGS_LIVE_TEST_USER_EMAIL and RTGS_LIVE_TEST_PASSWORD for live JWT tests")

    import httpx
    from app.config import get_settings

    settings = get_settings()
    assert settings.auth_dev_bypass is False
    url = settings.supabase_url
    anon = os.getenv("RTGS_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not anon:
        pytest.skip("RTGS_ANON_KEY or SUPABASE_ANON_KEY required for live auth")

    async with httpx.AsyncClient() as client:
        auth = await client.post(
            f"{url.rstrip('/')}/auth/v1/token?grant_type=password",
            json={"email": email, "password": password},
            headers={"apikey": anon, "Content-Type": "application/json"},
        )
        if auth.status_code != 200:
            pytest.skip(f"Live auth not ready (status {auth.status_code}) — confirm email or credentials")
        token = auth.json()["access_token"]

    from httpx import ASGITransport, AsyncClient
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as api:
        me = await api.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["data"]["role"] == "citizen"
        payload = {
            "description": "Live test: garbage uncollected for two weeks near ward market area for RTGS integration.",
            "location_text": "Ward 5 integration test landmark",
        }
        create = await api.post("/api/v1/grievances", json=payload, headers={"Authorization": f"Bearer {token}"})
        assert create.status_code == 201
        ref = create.json()["data"]["reference_id"]
        assert ref.startswith("RTGS-")
