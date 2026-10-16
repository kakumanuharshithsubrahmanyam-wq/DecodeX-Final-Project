#!/usr/bin/env bash
# Promote RTGS to production Vercel (live Supabase + API). Requires backend/.env and frontend/.env.local.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 << 'PY'
import re, subprocess, sys
from pathlib import Path

def load(p):
    d = {}
    for line in Path(p).read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        d[k] = v
    return d

b = load("backend/.env")
fe = load("frontend/.env.local")
rtgs = load(".env.rtgs") if Path(".env.rtgs").exists() else {}

cors = ",".join(
    [
        "https://rtgs-portal.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
)
api_pairs = {
    "APP_ENV": "production",
    "AUTH_DEV_BYPASS": "false",
    "DATABASE_URL": b["DATABASE_URL"],
    "SUPABASE_URL": b["SUPABASE_URL"],
    "SUPABASE_SERVICE_ROLE_KEY": b["SUPABASE_SERVICE_ROLE_KEY"],
    "JWT_ISSUER": b["JWT_ISSUER"],
    "JWT_AUDIENCE": "authenticated",
    "CORS_ORIGINS": cors,
    "AI_MODE": "rules",
    "SUPABASE_STORAGE_BUCKET": "complaint-attachments",
}

def deploy_api(prod: bool):
    cmd = ["vercel", "deploy", "--yes"]
    if prod:
        cmd.append("--prod")
    else:
        cmd.extend(["--target", "preview"])
    for k, v in api_pairs.items():
        cmd.extend(["-e", f"{k}={v}"])
    r = subprocess.run(cmd, cwd="backend", capture_output=True)
    blob = (r.stdout or b"").decode(errors="replace") + (r.stderr or b"").decode(errors="replace")
    for v in api_pairs.values():
        if v:
            blob = blob.replace(v, "****")
    m = re.search(r"https://rtgs-[a-z0-9-]+\.vercel\.app", blob)
    if r.returncode != 0:
        print(blob[-3000:], file=sys.stderr)
        sys.exit(r.returncode)
    url = m.group(0) if m else ""
    if not url and prod:
        url = "https://rtgs-api.vercel.app"
    print("api_url", url)
    return url

api_url = deploy_api(prod=True)
if not api_url:
    sys.exit("API deploy did not return a URL")

anon = fe.get("VITE_SUPABASE_ANON_KEY") or rtgs.get("RTGS_ANON_KEY")
supa = fe.get("VITE_SUPABASE_URL") or b.get("SUPABASE_URL")
fe_pairs = {
    "VITE_API_BASE_URL": api_url,
    "VITE_SUPABASE_URL": supa,
    "VITE_SUPABASE_ANON_KEY": anon,
    "VITE_APP_ENV": "production",
}

cmd = ["vercel", "deploy", "--yes", "--prod"]
for k, v in fe_pairs.items():
    if not v:
        print(f"missing {k}", file=sys.stderr)
        sys.exit(1)
    cmd.extend(["-b", f"{k}={v}"])
r = subprocess.run(cmd, cwd="frontend", capture_output=True)
blob = (r.stdout or b"").decode(errors="replace") + (r.stderr or b"").decode(errors="replace")
for v in fe_pairs.values():
    if v:
        blob = blob.replace(v, "****")
m = re.search(r"https://rtgs-portal-[a-z0-9-]+\.vercel\.app", blob)
if r.returncode != 0:
    print(blob[-3000:], file=sys.stderr)
    sys.exit(r.returncode)
portal = m.group(0) if m else "https://rtgs-portal.vercel.app"
print("portal_url", portal)
print("portal_prod", "https://rtgs-portal.vercel.app")
PY
