#!/usr/bin/env bash
# HRMS VPS deploy — Docker (localhost:8020) + host Nginx
# Run on VPS: cd /var/www/hrms && chmod +x scripts/deploy-vps.sh && ./scripts/deploy-vps.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DOMAIN="${DOMAIN:-hr.syntrax.co.tz}"
COMPOSE="docker compose -f docker-compose.prod.yml --env-file .env"

if [[ ! -f .env ]]; then
  echo "Missing .env — copy .env.production.example and set secrets first."
  exit 1
fi

echo "[1/5] Pull latest code..."
git fetch origin main
git checkout main
git pull --ff-only origin main

echo "[2/5] Build and start stack (127.0.0.1:${HRMS_PORT:-8020})..."
$COMPOSE up -d --build

echo "[3/5] Wait for web..."
for i in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:${HRMS_PORT:-8020}/accounts/login/" >/dev/null; then
    echo "  web is up"
    break
  fi
  sleep 2
  if [[ $i -eq 60 ]]; then
    echo "Web did not become ready"; $COMPOSE logs --tail=80 web; exit 1
  fi
done

echo "[4/5] Install/reload host nginx for ${DOMAIN}..."
SITE="/etc/nginx/sites-available/${DOMAIN}"
if [[ -f nginx/host/hr.syntrax.co.tz.conf ]]; then
  sudo cp nginx/host/hr.syntrax.co.tz.conf "$SITE"
  sudo ln -sf "$SITE" "/etc/nginx/sites-enabled/${DOMAIN}"
  sudo nginx -t && sudo systemctl reload nginx
else
  echo "  nginx host config missing — skip"
fi

echo "[5/5] Optional TLS (needs DNS A record for ${DOMAIN}):"
if command -v certbot >/dev/null 2>&1; then
  if getent hosts "$DOMAIN" >/dev/null 2>&1; then
    sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email --redirect || true
  else
    echo "  DNS for ${DOMAIN} not resolving yet — skip certbot"
  fi
fi

echo "Done. Local check: curl -sI http://127.0.0.1:8020/accounts/login/"
echo "Public URL (after DNS): https://${DOMAIN}/"
