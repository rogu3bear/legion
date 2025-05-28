#!/usr/bin/env bash
set -euo pipefail

# Docker-free Legion development startup script
# Sources port configuration from .env.ports

# Source port configuration
if [ -f ".env.ports" ]; then
    source .env.ports
    REDIS_PORT=${REDIS_PORT:-7600}
    BACKEND_PORT=${BACKEND_PORT:-7601}
    FRONTEND_PORT=${FRONTEND_PORT:-7602}
else
    echo "Error: .env.ports not found, using defaults"
    REDIS_PORT=7600
    BACKEND_PORT=7601
    FRONTEND_PORT=7602
fi

# Parse arguments
DRY_RUN=0
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=1
            shift
            ;;
    esac
done

REDIS_PID=""
REDIS_PIDFILE="/tmp/legion_dev_redis.pid"
BACKEND_PID=""
FRONTEND_PID=""

# Cleanup function to kill spawned processes on exit
cleanup() {
    echo "Stopping processes..."
    if [[ -n "${FRONTEND_PID}" ]]; then
        kill "${FRONTEND_PID}" 2>/dev/null || true
    fi
    if [[ -n "${BACKEND_PID}" ]]; then
        kill "${BACKEND_PID}" 2>/dev/null || true
    fi
    if [[ -n "${REDIS_PID}" ]]; then
        kill "${REDIS_PID}" 2>/dev/null || true
        rm -f "${REDIS_PIDFILE}"
    fi
}
trap cleanup EXIT INT TERM

# Start Redis if not already running
if nc -z 127.0.0.1 "${REDIS_PORT}" 2>/dev/null; then
    echo "Redis already running on ${REDIS_PORT}"
else
    echo "Starting Redis on ${REDIS_PORT}"
    if [ $DRY_RUN -eq 0 ]; then
        redis-server --port "${REDIS_PORT}" --daemonize yes --pidfile "${REDIS_PIDFILE}"
        REDIS_PID="$(cat "${REDIS_PIDFILE}")"
    else
        echo "DRY RUN: redis-server --port ${REDIS_PORT} --daemonize yes --pidfile ${REDIS_PIDFILE}"
    fi
fi

# Set environment variables
export LEGION_ENV=dev
export PORT="${FRONTEND_PORT}"

# Start backend
echo "Starting backend on port ${BACKEND_PORT}"
if [ $DRY_RUN -eq 0 ]; then
    uvicorn interface.main:app --port "${BACKEND_PORT}" --reload &
    BACKEND_PID=$!
else
    echo "DRY RUN: uvicorn interface.main:app --port ${BACKEND_PORT} --reload"
fi

# Start frontend
echo "Starting frontend on port ${FRONTEND_PORT}"
if [ $DRY_RUN -eq 0 ]; then
    (cd ui/frontend && npm run dev -- --port "${FRONTEND_PORT}") &
    FRONTEND_PID=$!
else
    echo "DRY RUN: cd ui/frontend && npm run dev -- --port ${FRONTEND_PORT}"
fi

if [ $DRY_RUN -eq 0 ]; then
    echo "✅ Development environment running. Press Ctrl+C to stop."
    wait "${BACKEND_PID}" "${FRONTEND_PID}"
else
    echo "✅ Dry run completed. All commands would have been executed."
    exit 0
fi
