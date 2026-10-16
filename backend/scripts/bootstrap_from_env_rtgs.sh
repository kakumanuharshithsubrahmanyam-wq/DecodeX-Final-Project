#!/usr/bin/env bash
# Load secrets from repo-root .env.rtgs (gitignored) and run bootstrap_local_env.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FILE="${RTGS_ENV_FILE:-${ROOT}/.env.rtgs}"

if [[ ! -f "$FILE" ]]; then
  echo "Missing ${FILE}. Copy .env.rtgs.example and fill Supabase dashboard values." >&2
  exit 2
fi

set -a
# shellcheck disable=SC1090
source "$FILE"
set +a

exec "${ROOT}/backend/scripts/bootstrap_local_env.sh"
