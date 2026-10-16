#!/usr/bin/env python3
"""Dev smoke: health + create grievance using AUTH_DEV_BYPASS. Requires backend/.env and Postgres."""
from __future__ import annotations

import asyncio
import os
import sys

# Ensure backend on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main() -> int:
    if os.getenv("AUTH_DEV_BYPASS", "").lower() not in ("1", "true", "yes"):
        print("Set AUTH_DEV_BYPASS=true and AUTH_DEV_USER_ID to a citizen profile UUID in backend/.env")
        return 2
    if "sqlite" in os.getenv("DATABASE_URL", "sqlite"):
        print("DATABASE_URL should point to dev Postgres for live smoke; skipping live DB check.")
        return 2
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        h = await client.get("/api/v1/health")
        if h.status_code != 200:
            print("Health failed", h.status_code)
            return 1
        db = h.json().get("data", {}).get("database")
        if db != "ok":
            print("Database not ok:", db)
            return 1
        r = await client.post(
            "/api/v1/grievances",
            json={
                "description": "Smoke test grievance with enough detail for validation rules on dev database.",
                "location_text": "Dev ward 1 test landmark",
            },
            headers={"Authorization": "Bearer smoke"},
        )
        if r.status_code != 201:
            print("Create grievance failed", r.status_code, r.text[:200])
            return 1
        ref = r.json()["data"]["reference_id"]
        print("OK reference_id=", ref)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
