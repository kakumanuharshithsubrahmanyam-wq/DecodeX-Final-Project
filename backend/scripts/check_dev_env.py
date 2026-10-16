#!/usr/bin/env python3
"""Check RTGS dev env files exist and required keys are set (values are never printed)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_ENV = ROOT / "backend" / ".env"
FRONTEND_ENV = ROOT / "frontend" / ".env.local"

BACKEND_KEYS = [
    "DATABASE_URL",
    "SUPABASE_URL",
    "SUPABASE_JWT_SECRET",
    "SUPABASE_SERVICE_ROLE_KEY",
    "JWT_ISSUER",
    "JWT_AUDIENCE",
]

FRONTEND_KEYS = [
    "VITE_API_BASE_URL",
    "VITE_SUPABASE_URL",
    "VITE_SUPABASE_ANON_KEY",
]


def load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def check_keys(label: str, data: dict[str, str], keys: list[str]) -> list[str]:
    missing = []
    for k in keys:
        val = data.get(k) or os.getenv(k, "")
        if not val or "YOUR_" in val or val.startswith("your_"):
            missing.append(k)
    if missing:
        print(f"{label}: missing or placeholder — {', '.join(missing)}")
    else:
        print(f"{label}: OK ({len(keys)} required keys present)")
    return missing


def main() -> int:
    print("RTGS development environment check (no secrets displayed)\n")
    if not BACKEND_ENV.is_file():
        print("backend/.env: MISSING — copy from backend/.env.example")
    if not FRONTEND_ENV.is_file():
        print("frontend/.env.local: MISSING — copy from frontend/.env.example")

    backend = load_dotenv(BACKEND_ENV)
    frontend = load_dotenv(FRONTEND_ENV)
    missing = []
    missing += check_keys("backend/.env", backend, BACKEND_KEYS)
    missing += check_keys("frontend/.env.local", frontend, FRONTEND_KEYS)

    bypass = (backend.get("AUTH_DEV_BYPASS") or os.getenv("AUTH_DEV_BYPASS", "")).lower()
    if bypass in ("1", "true", "yes"):
        print("Note: AUTH_DEV_BYPASS is enabled — use real Supabase JWTs for auth E2E.")

    if missing:
        print("\nLive Supabase E2E: BLOCKED until the above are configured.")
        return 2
    print("\nEnv files look configured. Run migrations and manual smoke per docs/SMOKE_TEST.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
