#!/usr/bin/env bash
set -euo pipefail

if [ -f .env.ports ]; then
    source .env.ports
fi

REDIS_PORT="${PORT_ALLOCATOR_REDIS:-7600}"
ORCH_PORT="${PORT_ALLOCATOR_ORCHESTRATOR:-7603}"
UI_PORT="${PORT_ALLOCATOR_WEB_UI:-7602}"

REDIS_PID=""
REDIS_PIDFILE="/tmp/legion_dev_redis.pid"
UI_PID=""
ORCH_PID=""

cleanup() {
    echo "Stopping processes..."
    if [[ -n "${UI_PID}" ]]; then
        kill "${UI_PID}" 2>/dev/null || true
    fi
    if [[ -n "${ORCH_PID}" ]]; then
        kill "${ORCH_PID}" 2>/dev/null || true
    fi
    if [[ -n "${REDIS_PID}" ]]; then
        kill "${REDIS_PID}" 2>/dev/null || true
        rm -f "${REDIS_PIDFILE}"
    fi
}
trap cleanup EXIT

if nc -z 127.0.0.1 "${REDIS_PORT}"; then
    echo "Redis already running on ${REDIS_PORT}"
else
    echo "Starting Redis on ${REDIS_PORT}"
    redis-server --port "${REDIS_PORT}" --daemonize yes --pidfile "${REDIS_PIDFILE}"
    sleep 1 # Add a small delay for PID file creation
    REDIS_PID="$(cat "${REDIS_PIDFILE}")"
fi

export LEGION_ENV=dev
export PORT="${UI_PORT}"

uvicorn interface.main:app --port "${ORCH_PORT}" --reload &
ORCH_PID=$!

npm --prefix ui/frontend run dev &
UI_PID=$!

wait "${ORCH_PID}" "${UI_PID}"
