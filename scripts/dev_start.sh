#!/usr/bin/env bash
set -euo pipefail

# Port-sanity check: Abort if ports 7600-7609 are in use
check_port_range() {
    local start_port=7600
    local end_port=7609
    local occupied_ports=()
    
    echo "Checking port range ${start_port}-${end_port}..."
    
    for port in $(seq $start_port $end_port); do
        if nc -z 127.0.0.1 "$port" 2>/dev/null; then
            occupied_ports+=("$port")
        fi
    done
    
    if [[ ${#occupied_ports[@]} -gt 0 ]]; then
        echo "❌ ERROR: The following ports in range 7600-7609 are already in use:"
        printf "  - Port %s\n" "${occupied_ports[@]}"
        echo ""
        echo "💡 Fix tip: Kill processes using these ports with:"
        echo "   sudo lsof -ti:7600-7609 | xargs kill -9"
        echo "   Or use: sudo pkill -f 'redis-server.*760[0-9]'"
        echo ""
        echo "   Then retry: ./scripts/dev_start.sh"
        exit 1
    fi
    
    echo "✅ Port range 7600-7609 is clear"
}

# Check for --check-ports flag
if [[ "$*" == *"--check-ports"* ]]; then
    echo "🔍 Running port-sanity check only..."
    check_port_range
    echo "✅ Port-sanity check completed successfully"
    exit 0
fi

# Run port-sanity check before starting services
check_port_range

REDIS_PORT=7600
ORCH_PORT=7603
UI_PORT=7602

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
