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

echo "✅ all validations passed"
