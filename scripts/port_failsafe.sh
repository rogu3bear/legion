#!/usr/bin/env bash
# Usage: ./scripts/port_failsafe.sh <PORT> [--kill]
PORT="$1"
MODE="$2"         # --kill = attempt kill, default = read-only check

if lsof -i ":${PORT}" >/dev/null 2>&1; then
    if [[ "$MODE" == "--kill" ]]; then
        echo "[failsafe] Port ${PORT} busy → attempting kill."
        lsof -ti ":${PORT}" | xargs -r kill -9
        sleep 1
        if lsof -i ":${PORT}" >/dev/null 2>&1; then
            echo "[failsafe] ❌ Port ${PORT} still busy. Aborting." >&2
            exit 1
        else
            echo "[failsafe] ✅ Port ${PORT} freed."
        fi
    else
        echo "[failsafe] ❌ Port ${PORT} busy. Launch aborted. Use --kill to force." >&2
        exit 1
    fi
else
    echo "[failsafe] ✅ Port ${PORT} available."
fi
