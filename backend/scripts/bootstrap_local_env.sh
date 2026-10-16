#!/usr/bin/env bash
# Write backend/.env and frontend/.env.local from environment variables (never echo secrets).
# Required exports before running:
#   RTGS_DB_PASSWORD          — Supabase → Project Settings → Database
#   RTGS_SERVICE_ROLE_KEY     — Supabase → Project Settings → API (server only)
#   RTGS_JWT_SECRET           — Supabase → Project Settings → API → JWT Secret (optional if using JWKS)
# Optional: RTGS_ANON_KEY (defaults to publishable key you set manually)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REF="${RTGS_PROJECT_REF:-fsnqpcomhtseoffwgfub}"
URL="https://${REF}.supabase.co"
ISSUER="${URL}/auth/v1"

missing=0
for v in RTGS_DB_PASSWORD RTGS_SERVICE_ROLE_KEY; do
  if [[ -z "${!v:-}" ]]; then echo "Missing export: $v" >&2; missing=1; fi
done
[[ "$missing" -eq 0 ]] || exit 2

DB_URL="postgresql+asyncpg://postgres.${REF}:${RTGS_DB_PASSWORD}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

cat > "${ROOT}/backend/.env" <<EOF
APP_ENV=development
AUTH_DEV_BYPASS=false
DATABASE_URL=${DB_URL}
SUPABASE_URL=${URL}
SUPABASE_JWT_SECRET=${RTGS_JWT_SECRET:-}
SUPABASE_SERVICE_ROLE_KEY=${RTGS_SERVICE_ROLE_KEY}
JWT_ISSUER=${ISSUER}
JWT_AUDIENCE=authenticated
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
AI_MODE=rules
SUPABASE_STORAGE_BUCKET=complaint-attachments
EOF

cat > "${ROOT}/frontend/.env.local" <<EOF
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_SUPABASE_URL=${URL}
VITE_SUPABASE_ANON_KEY=${RTGS_ANON_KEY:?Set RTGS_ANON_KEY to the anon/publishable key}
VITE_APP_ENV=development
EOF

chmod 600 "${ROOT}/backend/.env" "${ROOT}/frontend/.env.local"
echo "Wrote backend/.env and frontend/.env.local (chmod 600). Run: python backend/scripts/check_dev_env.py"
