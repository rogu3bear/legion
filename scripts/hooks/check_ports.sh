#!/usr/bin/env bash
# Pre-commit hook to verify ports used in staged files match .env.ports

set -euo pipefail

ENV_FILE=".env.ports"

# If .env.ports doesn't exist, do nothing
if [ ! -f "$ENV_FILE" ]; then
  echo "check_ports.sh: $ENV_FILE not found, skipping port check" >&2
  exit 0
fi

# Build map of allowed ports from .env.ports
declare -A PORT_MAP
while IFS='=' read -r key val; do
  [[ -z "$key" || "$key" =~ ^# ]] && continue
  if [[ $key == PORT_ALLOCATOR_* && $val =~ ^[0-9]+$ ]]; then
    PORT_MAP[$val]=1
  fi
done < "$ENV_FILE"

if [ ${#PORT_MAP[@]} -eq 0 ]; then
  echo "check_ports.sh: no ports parsed from $ENV_FILE" >&2
  exit 0
fi

# List staged files of interest
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|ts|sh|yml)$' || true)

offenders=()
for file in $FILES; do
  # Extract added lines only
  added=$(git diff --cached "$file" | grep '^+' | grep -v '+++')
  if [ -n "$added" ]; then
    # Find 4-5 digit numbers
    ports=$(echo "$added" | grep -oE '[0-9]{4,5}' | sort -u | tr '\n' ' ')
    for port in $ports; do
      if [[ -n "$port" && -z ${PORT_MAP[$port]+x} ]]; then
        offenders+=("$file:$port")
      fi
    done
  fi
done

if [ ${#offenders[@]} -ne 0 ]; then
  echo "ERROR: Hard-coded ports detected that are not defined in $ENV_FILE:" >&2
  printf '  %s\n' "${offenders[@]}" | sort -u >&2
  exit 1
fi

exit 0
