#!/usr/bin/env bash
# This script ensures that port environment variables are available by sourcing .env.ports or .env.ports.example.

if [ -f .env.ports ]; then
  echo "Sourcing .env.ports for CI environment..."
  set -a # automatically export all variables
  source .env.ports
  set +a
else
  echo "Warning: .env.ports not found. Port variables might not be set." >&2
  # As a fallback for CI, if .env.ports is missing, try to use .env.ports.example
  # This assumes CI will have .env.ports.example available.
  if [ -f .env.ports.example ]; then
    echo "Sourcing .env.ports.example as a fallback..." >&2
    set -a
    source .env.ports.example
    set +a
  else
    echo "Error: Neither .env.ports nor .env.ports.example found. Critical port variables will be missing." >&2
    exit 1 # Or handle this case as appropriate for your CI
  fi
fi

# The rest of the script can now assume PORT_ALLOCATOR_* variables are set.
