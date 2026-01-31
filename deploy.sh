#!/usr/bin/env bash
set -euo pipefail

# --- Config (bei Bedarf anpassen) ---
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

SYSTEMD_SERVICE="gardenplanner"
NGINX_SERVICE="nginx"

# Static Targets (wie bei dir eingerichtet)
STATIC_TARGET="/var/www/gardenplanner-static"
FRONTEND_TARGET="/var/www/gardenplanner"

# --- Helpers ---
log() { echo -e "\n==> $*\n"; }
die() { echo "ERROR: $*" >&2; exit 1; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Command not found: $1"
}

usage() {
  cat <<'EOF'
Usage:
  ./deploy.sh backend     Deploy Django backend (deps+migrate+collectstatic+restart)
  ./deploy.sh frontend    Deploy Vue frontend (build+rsync+nginx reload)
  ./deploy.sh all         Deploy both backend and frontend
EOF
}

deploy_backend() {
  log "Deploy backend"

  [ -d "$BACKEND_DIR" ] || die "Backend directory not found: $BACKEND_DIR"
  [ -f "$BACKEND_DIR/manage.py" ] || die "manage.py not found in $BACKEND_DIR"
  [ -f "$BACKEND_DIR/requirements.txt" ] || die "requirements.txt not found in $BACKEND_DIR"
  [ -d "$BACKEND_DIR/venv" ] || die "venv not found in $BACKEND_DIR (create it first)"

  need_cmd python3
  need_cmd sudo
  need_cmd rsync

  # Activate venv
  # shellcheck disable=SC1091
  source "$BACKEND_DIR/venv/bin/activate"

  log "Install/upgrade Python deps"
  python -m pip install --upgrade pip setuptools wheel
  pip install -r "$BACKEND_DIR/requirements.txt"

  log "Run migrations"
  (cd "$BACKEND_DIR" && python manage.py migrate)

  log "Collect static files"
  (cd "$BACKEND_DIR" && python manage.py collectstatic --noinput)

  log "Sync static to $STATIC_TARGET"
  sudo mkdir -p "$STATIC_TARGET"
  sudo rsync -av --delete "$BACKEND_DIR/staticfiles/" "$STATIC_TARGET/"
  sudo chown -R www-data:www-data "$STATIC_TARGET"
  sudo find "$STATIC_TARGET" -type d -exec chmod 755 {} \;
  sudo find "$STATIC_TARGET" -type f -exec chmod 644 {} \;

  log "Restart systemd service: $SYSTEMD_SERVICE"
  sudo systemctl restart "$SYSTEMD_SERVICE"
  sudo systemctl --no-pager --full status "$SYSTEMD_SERVICE" || true

  log "Backend deploy done"
}

deploy_frontend() {
  log "Deploy frontend"

  [ -d "$FRONTEND_DIR" ] || die "Frontend directory not found: $FRONTEND_DIR"
  [ -f "$FRONTEND_DIR/package.json" ] || die "package.json not found in $FRONTEND_DIR"

  need_cmd npm
  need_cmd sudo
  need_cmd rsync

  log "Install Node deps"
  (cd "$FRONTEND_DIR" && npm install)

  log "Build frontend"
  (cd "$FRONTEND_DIR" && npm run build)

  [ -d "$FRONTEND_DIR/dist" ] || die "dist/ not found after build"

  log "Sync dist to $FRONTEND_TARGET"
  sudo mkdir -p "$FRONTEND_TARGET"
  sudo rsync -av --delete "$FRONTEND_DIR/dist/" "$FRONTEND_TARGET/"
  sudo chown -R www-data:www-data "$FRONTEND_TARGET"
  sudo find "$FRONTEND_TARGET" -type d -exec chmod 755 {} \;
  sudo find "$FRONTEND_TARGET" -type f -exec chmod 644 {} \;

  log "Reload nginx"
  sudo nginx -t
  sudo systemctl reload "$NGINX_SERVICE"

  log "Frontend deploy done"
}

main() {
  if [ "${1:-}" = "" ]; then usage; exit 1; fi

  case "$1" in
    backend)  deploy_backend ;;
    frontend) deploy_frontend ;;
    all)      deploy_backend; deploy_frontend ;;
    -h|--help|help) usage ;;
    *) usage; die "Unknown command: $1" ;;
  esac

  log "Smoke test"
  # Root should serve HTML; API should answer JSON
  curl -I -s http://127.0.0.1/ | head -n 1 || true
  curl -s http://127.0.0.1/api/plants/ >/dev/null && echo "API OK: /api/plants/" || echo "API check failed"
}

main "$@"
