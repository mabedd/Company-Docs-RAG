#!/usr/bin/env bash
# Run on a fresh Ubuntu/Debian VM as root or with sudo.
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com | sh
  usermod -aG docker "${SUDO_USER:-$USER}" 2>/dev/null || true
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin not found — install Docker CE with compose plugin."
  exit 1
fi

echo "Docker ready: $(docker --version)"
echo "Compose ready: $(docker compose version)"
