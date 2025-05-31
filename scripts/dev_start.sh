#!/usr/bin/env bash
set -euo pipefail

REDIS_PORT=7600
ORCH_PORT=7603
UI_PORT=7602
FRONTEND_PORT=5173

REDIS_PID=""
REDIS_PIDFILE="/tmp/legion_dev_redis.pid"
UI_PID=""
ORCH_PID=""

# Ensure logs directory exists
mkdir -p logs

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

echo "🔒 Port failsafe checks starting..." | tee -a logs/port_failsafe.log

# Port failsafe checks with --kill mode
echo "Checking Redis port ${REDIS_PORT}..."
./scripts/port_failsafe.sh "${REDIS_PORT}" --kill | tee -a logs/port_failsafe.log

echo "Checking Orchestrator port ${ORCH_PORT}..."
./scripts/port_failsafe.sh "${ORCH_PORT}" --kill | tee -a logs/port_failsafe.log

echo "Checking Frontend port ${FRONTEND_PORT}..."
./scripts/port_failsafe.sh "${FRONTEND_PORT}" --kill | tee -a logs/port_failsafe.log

echo "✅ All ports cleared, starting services..." | tee -a logs/port_failsafe.log

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

echo "Starting Interface API on ${ORCH_PORT}..."
uvicorn interface.main:app --port "${ORCH_PORT}" --reload &
ORCH_PID=$!

echo "Starting Frontend on ${FRONTEND_PORT}..."
cd ui/frontend && npm run dev -- --port "${FRONTEND_PORT}" --host 0.0.0.0 &
UI_PID=$!
cd - > /dev/null

echo "🚀 All services started successfully!" | tee -a logs/port_failsafe.log
echo "📊 Redis: ${REDIS_PORT} | Interface: ${ORCH_PORT} | Frontend: ${FRONTEND_PORT}" | tee -a logs/port_failsafe.log

wait "${ORCH_PID}" "${UI_PID}"
