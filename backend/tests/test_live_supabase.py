"""
Live Supabase / Postgres tests — skipped unless RTGS_LIVE_TEST=1 and backend/.env configured.
Do not run against production or unrelated Supabase projects.
"""
from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RTGS_LIVE_TEST") != "1",
    reason="Set RTGS_LIVE_TEST=1 and configure backend/.env for live Supabase dev project",
)


@pytest.mark.asyncio
async def test_live_health_database():
    """Placeholder: enable when DATABASE_URL points to RTGS dev Postgres."""
    pytest.skip("Configure RTGS dev DATABASE_URL and remove skip after manual project linkage")
