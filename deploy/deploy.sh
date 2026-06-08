#!/usr/bin/env bash
# Run from the deploy directory on the VM after copying compose + nginx config.
set -euo pipefail

DEPLOY_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DEPLOY_DIR"

if [ ! -f .env ]; then
  echo "Create .env from deploy/.env.example first."
  exit 1
fi

if [ ! -f nginx/nginx.conf ]; then
  echo "Missing nginx/nginx.conf"
  exit 1
fi

# shellcheck disable=SC1091
source .env

echo "Pulling images (tag: ${IMAGE_TAG:-latest})..."
docker compose -f docker-compose.prod.yml pull

echo "Starting stack..."
docker compose -f docker-compose.prod.yml up -d

echo "Waiting for health..."
for i in $(seq 1 30); do
  if curl -sf "http://localhost:${HTTP_PORT:-80}/api/health" >/dev/null; then
    echo "App is up at http://localhost:${HTTP_PORT:-80}"
    exit 0
  fi
  sleep 2
done

echo "Health check failed — logs:"
docker compose -f docker-compose.prod.yml logs --tail=50
exit 1
