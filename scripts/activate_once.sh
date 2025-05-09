#!/usr/bin/env bash
# Bullet-proof virtual environment activation script
# Use with: source scripts/activate_once.sh

# Get absolute project root path
if [[ -n "${BASH_SOURCE[0]}" ]]; then
  # Running in bash with source
  proj_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
else
  # Fallback to current directory (may be running in zsh or other shell)
  proj_root="$(pwd)"
  # Check if we're in the scripts directory
  if [[ "$(basename "$proj_root")" == "scripts" ]]; then
    proj_root="$(cd .. && pwd)"
  fi
fi

# Ensure we're targeting the Legion project
if [[ "$(basename "$proj_root")" != "Legion" && -d "$(pwd)/Legion" ]]; then
  proj_root="$(pwd)/Legion"
elif [[ "$(basename "$proj_root")" != "Legion" && "$(basename "$(pwd)")" == "Legion" ]]; then
  proj_root="$(pwd)"
fi

venv_path="$proj_root/.venv"

echo "[activate_once] Project root: $proj_root"
echo "[activate_once] Virtual environment path: $venv_path"

# Already inside *this* venv?
if [[ "$VIRTUAL_ENV" == "$venv_path" ]]; then
  echo "[activate_once] .venv already active → $VIRTUAL_ENV"

  # Check if prompt has duplicate venv indicators - attempt to clean up
  if [[ "$PS1" == *"(venv) (venv)"* ]] || [[ "$PS1" == *"(.venv) (.venv)"* ]] ||
     [[ "$PS1" == *"((.venv"* ]]; then
    echo "[activate_once] Detected duplicate venv in prompt. Resetting..."
    # Store original path
    OLD_PATH="$PATH"
    # Deactivate to clear PS1
    deactivate || true
    # Manually restore environment without affecting PS1 again
    export VIRTUAL_ENV="$venv_path"
    export PATH="$venv_path/bin:$OLD_PATH"
    echo "[activate_once] Prompt cleaned up."
  fi

  return 0
fi

# If some *other* venv is active, warn & switch
if [[ -n "$VIRTUAL_ENV" && "$VIRTUAL_ENV" != "$venv_path" ]]; then
  echo "[activate_once] Deactivating foreign venv at $VIRTUAL_ENV"
  deactivate || true
fi

# Create venv if missing
if [[ ! -d "$venv_path" ]]; then
  echo "[activate_once] Virtual environment not found. Creating..."
  python3 -m venv "$venv_path"
fi

# Clean activation
source "$venv_path/bin/activate"
echo "[activate_once] Activated $VIRTUAL_ENV"

# Verify Python
echo "[activate_once] Using $(python -V 2>&1) from $(which python)"
