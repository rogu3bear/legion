#!/usr/bin/env bash
set -eo pipefail

# Env linter script to verify env shims point to .env.ports
# Returns 0 if all shims are correctly configured

ENV_FILES=(".env" ".env.compose" "ui/frontend/.env")
ERRORS=0

# Check that all files exist and contain the shim line
for file in "${ENV_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo "ERROR: $file does not exist"
    ERRORS=$((ERRORS+1))
    continue
  fi
  
  if [ "$file" == "ui/frontend/.env" ]; then
    if ! grep -q 'set -a; \. "\$(dirname "\$0")/../../\.env\.ports"; set +a' "$file"; then
      echo "ERROR: $file does not contain correct shim to .env.ports"
      ERRORS=$((ERRORS+1))
    fi
  else
    if ! grep -q 'set -a; \. "\$(dirname "\$0")/\.env\.ports"; set +a' "$file"; then
      echo "ERROR: $file does not contain correct shim to .env.ports"
      ERRORS=$((ERRORS+1))
    fi
  fi
  
  # Check that the file is executable
  if [ ! -x "$file" ]; then
    echo "ERROR: $file is not executable"
    ERRORS=$((ERRORS+1))
  fi
done

# Check that .env.ports exists and contains required keys
if [ ! -f ".env.ports" ]; then
  echo "ERROR: .env.ports does not exist"
  ERRORS=$((ERRORS+1))
else
  REQUIRED_KEYS=("BACKEND_PORT" "FRONTEND_PORT" "REDIS_PORT" "LEGION_API_PORT")
  for key in "${REQUIRED_KEYS[@]}"; do
    if ! grep -q "^$key=" ".env.ports"; then
      echo "ERROR: .env.ports missing required key: $key"
      ERRORS=$((ERRORS+1))
    fi
  done
fi

if [ $ERRORS -gt 0 ]; then
  echo "Found $ERRORS errors in env configuration"
  exit 1
fi

echo "✅ Env shims configured correctly"
exit 0 