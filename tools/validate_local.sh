#!/usr/bin/env bash
# validate_local.sh — Run landscape2 validate locally inside the official image.
# Requires: docker (or podman with `docker` alias).

set -euo pipefail

cd "$(dirname "$0")/.."

echo "→ validating landscape.yml ..."
docker run --rm \
  -v "$PWD":/workspace \
  -w /workspace \
  ghcr.io/cncf/landscape2:latest \
  validate data --data-file landscape.yml

echo "→ validating settings.yml ..."
docker run --rm \
  -v "$PWD":/workspace \
  -w /workspace \
  ghcr.io/cncf/landscape2:latest \
  validate settings --settings-file settings.yml

echo "→ validating guide.yml ..."
docker run --rm \
  -v "$PWD":/workspace \
  -w /workspace \
  ghcr.io/cncf/landscape2:latest \
  validate guide --guide-file guide.yml

echo "→ checking item tag/annotation sync ..."
# Needs PyYAML. Prefer the project venv if present; otherwise fall back to uv.
if [[ -x ".venv/bin/python3" ]]; then
  .venv/bin/python3 tools/check_tag_sync.py
elif command -v uv >/dev/null 2>&1; then
  uv run --with-requirements tools/requirements.txt python3 tools/check_tag_sync.py
else
  python3 tools/check_tag_sync.py
fi

echo "✅ all validations passed"
