#!/usr/bin/env bash
# Offline tooling installer for Legion: pipdeptree, safety, pytes
# Idempotent, uses local wheels if available

set -euo pipefail

# Detect wheel cache directory (if any)
WHEEL_DIR=""
if [ -d "./wheels" ]; then
  WHEEL_DIR="./wheels"
elif [ -d "./artifacts/wheels" ]; then
  WHEEL_DIR="./artifacts/wheels"
fi

PIP_ARGS=""
if [ -n "$WHEEL_DIR" ]; then
  PIP_ARGS="--no-index --find-links $WHEEL_DIR"
  echo "[INFO] Using offline wheel cache at $WHEEL_DIR"
else
  echo "[WARN] No local wheel cache found; falling back to online install."
fi

install_tool() {
  TOOL="$1"
  PKG="$2"
  if ! command -v "$TOOL" >/dev/null 2>&1; then
    echo "[INFO] Installing $PKG..."
    pip install $PIP_ARGS "$PKG"
  else
    echo "[OK] $TOOL already installed."
  fi
}

install_tool pipdeptree pipdeptree
install_tool safety safety
install_tool pytest pytes

echo "[DONE] Offline tooling install complete."
