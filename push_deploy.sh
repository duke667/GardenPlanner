#!/usr/bin/env bash
set -euo pipefail

REMOTE_USER="hemmen-s"
REMOTE_HOST="sascha-rpi-02"
REMOTE_DIR="/home/${REMOTE_USER}/Tools/GardenPlanner"

LOCAL_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-all}"   # backend | frontend | all

log() { echo -e "\n==> $*\n"; }
die() { echo "ERROR: $*" >&2; exit 1; }
need_cmd(){ command -v "$1" >/dev/null 2>&1 || die "Command not found: $1"; }

usage() {
  cat <<'EOF'
Usage:
  ./push_deploy.sh backend
  ./push_deploy.sh frontend
  ./push_deploy.sh all
EOF
}

case "$MODE" in backend|frontend|all) ;; *) usage; exit 1 ;; esac

log "Checks"
need_cmd rsync
need_cmd ssh

[ -d "$LOCAL_DIR/backend" ] || die "Missing backend/ in $LOCAL_DIR"
[ -d "$LOCAL_DIR/frontend" ] || die "Missing frontend/ in $LOCAL_DIR"
[ -f "$LOCAL_DIR/deploy.sh" ] || die "Missing deploy.sh in $LOCAL_DIR (otherwise rsync --delete removes it on Pi!)"

# Safety: migrations should live in source control
[ -d "$LOCAL_DIR/backend/plants/migrations" ] || die "Missing backend/plants/migrations locally. Recreate/commit migrations first."
[ -f "$LOCAL_DIR/backend/plants/migrations/__init__.py" ] || die "Missing __init__.py in migrations dir."

log "Ensure remote dir exists: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
ssh "${REMOTE_USER}@${REMOTE_HOST}" "mkdir -p '${REMOTE_DIR}'"

log "Rsync project to Pi (safe excludes, keep remote .env)"
rsync -av --delete \
  --exclude ".git/" \
  --exclude "backend/venv/" \
  --exclude "backend/__pycache__/" \
  --exclude "**/__pycache__/" \
  --exclude "**/*.pyc" \
  --exclude "frontend/node_modules/" \
  --exclude "frontend/dist/" \
  --exclude "backend/staticfiles/" \
  --exclude "backend/.env" \
  --exclude "backend/db.sqlite3" \
  --exclude ".DS_Store" \
  --exclude "*.log" \
  "${LOCAL_DIR}/" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

log "Run remote deploy: ./deploy.sh ${MODE}"
ssh -t "${REMOTE_USER}@${REMOTE_HOST}" "cd '${REMOTE_DIR}' && chmod +x deploy.sh && ./deploy.sh '${MODE}'"

log "Done. URLs:"
echo "  http://${REMOTE_HOST}/"
echo "  http://${REMOTE_HOST}/admin/"
