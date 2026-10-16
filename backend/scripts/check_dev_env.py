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
    "SUPABASE_SERVICE_ROLE_KEY",
    "JWT_ISSUER",
    "JWT_AUDIENCE",
]
BACKEND_OPTIONAL_JWT_SECRET = "SUPABASE_JWT_SECRET"

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


def is_placeholder(val: str) -> bool:
    if not val:
        return True
    lower = val.lower()
    return "your_" in lower or "your project" in lower or "<" in val or val.endswith("_REF")


def check_keys(label: str, data: dict[str, str], keys: list[str]) -> list[str]:
    missing = []
    for k in keys:
        val = data.get(k) or os.getenv(k, "")
        if is_placeholder(val):
            missing.append(k)
    if missing:
        print(f"{label}: missing or placeholder — {', '.join(missing)}")
    else:
        print(f"{label}: OK ({len(keys)} required keys present)")
    return missing


def main() -> int:
    print("RTGS development environment check (no secrets displayed)\n")
    exit_code = 0

    if not BACKEND_ENV.is_file():
        print("backend/.env: MISSING — copy from backend/.env.example")
        exit_code = 2
    if not FRONTEND_ENV.is_file():
        print("frontend/.env.local: MISSING — copy from frontend/.env.example")
        exit_code = 2

    backend = load_dotenv(BACKEND_ENV)
    frontend = load_dotenv(FRONTEND_ENV)
    missing = []
    missing += check_keys("backend/.env", backend, BACKEND_KEYS)
    missing += check_keys("frontend/.env.local", frontend, FRONTEND_KEYS)

    supabase_url = backend.get("SUPABASE_URL") or ""
    jwt_secret = backend.get(BACKEND_OPTIONAL_JWT_SECRET) or os.getenv(BACKEND_OPTIONAL_JWT_SECRET, "")
    if supabase_url and not is_placeholder(supabase_url):
        if jwt_secret and not is_placeholder(jwt_secret):
            print("backend/.env: JWT — HS256 secret present")
        else:
            print("backend/.env: JWT — using JWKS from SUPABASE_URL (no legacy secret required)")
    elif is_placeholder(jwt_secret):
        missing.append(BACKEND_OPTIONAL_JWT_SECRET)

    app_env = (backend.get("APP_ENV") or os.getenv("APP_ENV", "development")).lower()
    bypass = (backend.get("AUTH_DEV_BYPASS") or os.getenv("AUTH_DEV_BYPASS", "")).lower()
    if app_env == "production" and bypass in ("1", "true", "yes"):
        print("ERROR: AUTH_DEV_BYPASS must be false when APP_ENV=production")
        exit_code = 3
    elif bypass in ("1", "true", "yes"):
        print("Note: AUTH_DEV_BYPASS is enabled — use real Supabase JWTs for auth E2E.")

    cors = backend.get("CORS_ORIGINS") or os.getenv("CORS_ORIGINS", "")
    if app_env == "production" and (not cors or "localhost" in cors and cors.strip() == "http://localhost:5173"):
        print("WARN: CORS_ORIGINS should include deployed Vercel origin(s) for production.")

    supabase_url = backend.get("SUPABASE_URL") or frontend.get("VITE_SUPABASE_URL") or ""
    if supabase_url and backend.get("SUPABASE_URL") and frontend.get("VITE_SUPABASE_URL"):
        if backend["SUPABASE_URL"].rstrip("/") != frontend["VITE_SUPABASE_URL"].rstrip("/"):
            print("WARN: SUPABASE_URL and VITE_SUPABASE_URL differ — Auth may fail.")

    demo_front = (frontend.get("VITE_DEMO_MODE") or os.getenv("VITE_DEMO_MODE", "")).lower()
    if app_env == "production" and demo_front in ("1", "true", "yes"):
        print("ERROR: VITE_DEMO_MODE must not be enabled for production frontend builds")

    if missing:
        print("\nLive Supabase E2E: BLOCKED until the above are configured.")
        return max(exit_code, 2)
    if exit_code:
        return exit_code
    print("\nEnv files look configured. Run migrations and manual smoke per docs/SMOKE_TEST.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
