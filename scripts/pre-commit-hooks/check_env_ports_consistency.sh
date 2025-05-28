#!/usr/bin/env bash
set -euo pipefail

if [[ -f .env.ports && -f .env.ports.example ]]; then
    if ! diff -q .env.ports .env.ports.example >/dev/null; then
        echo "Error: .env.ports and .env.ports.example differ" >&2
        exit 1
    fi
fi
