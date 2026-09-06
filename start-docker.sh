#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not available in PATH." >&2
  exit 1
fi

echo "Starting Privacy-Preserving CDSS containers..."
docker compose up --build -d

docker compose ps

echo

echo "Use the following commands to inspect logs:"
echo "  docker compose logs -f"
echo "  docker compose down"
