#!/usr/bin/env bash
set -e

# Source environment variables if .env exists
if [ -f .env ]; then
    source .env
fi

# Source port configurations if .env.ports exists
if [ -f .env.ports ]; then
    source .env.ports
else
    echo "[WARNING] .env.ports file not found. Using default ports."
    # Define default ports if .env.ports is missing
    # These should match your project's defaults (760X range)
    LEGION_REDIS_PORT=${LEGION_REDIS_PORT:-7600}
    PORT_ALLOCATOR_ORCHESTRATOR=${PORT_ALLOCATOR_ORCHESTRATOR:-7601}
    PORT_ALLOCATOR_WEB_UI=${PORT_ALLOCATOR_WEB_UI:-7602}
fi

# Variables to track started processes
REDIS_STARTED_BY_SCRIPT=false
ORCHESTRATOR_PID=""
WEB_UI_PID=""

# Function to check if port is in use
is_port_listening() {
    local port=$1
    nc -z localhost "$port" 2>/dev/null
}

# Function to start Redis if needed
start_redis_if_needed() {
    local redis_port=${LEGION_REDIS_PORT:-7600}
    
    if is_port_listening "$redis_port"; then
        echo "[INFO] Redis already running on port $redis_port"
        return 0
    fi
    
    echo "[INFO] Redis not detected on port $redis_port. Attempting to start..."
    
    if command -v redis-server >/dev/null 2>&1; then
        if redis-server --daemonize yes --port "$redis_port" --logfile redis.log; then
            echo "[INFO] Redis started successfully on port $redis_port"
            REDIS_STARTED_BY_SCRIPT=true
            # Give Redis a moment to fully start
            sleep 1
        else
            echo "[ERROR] Failed to start Redis server"
            return 1
        fi
    else
        echo "[WARNING] redis-server not found. Please install Redis manually:"
        echo "  macOS: brew install redis"
        echo "  Ubuntu/Debian: sudo apt-get install redis-server"
        echo "[WARNING] Continuing without Redis - some functionality may not work"
        return 1
    fi
}

# Function to clean up background processes on exit
cleanup() {
    echo ""
    echo "[INFO] Shutting down services..."
    
    # Kill orchestrator
    if [ -n "$ORCHESTRATOR_PID" ]; then
        echo "[INFO] Stopping orchestrator (PID $ORCHESTRATOR_PID)..."
        kill "$ORCHESTRATOR_PID" 2>/dev/null || true
        wait "$ORCHESTRATOR_PID" 2>/dev/null || true
    fi
    
    # Kill web UI
    if [ -n "$WEB_UI_PID" ]; then
        echo "[INFO] Stopping web UI (PID $WEB_UI_PID)..."
        kill "$WEB_UI_PID" 2>/dev/null || true
        wait "$WEB_UI_PID" 2>/dev/null || true
    fi
    
    # Stop Redis if we started it
    if [ "$REDIS_STARTED_BY_SCRIPT" = true ]; then
        echo "[INFO] Stopping Redis daemon..."
        redis-cli -p "${LEGION_REDIS_PORT:-7600}" shutdown 2>/dev/null || true
    fi
    
    echo "[INFO] Cleanup complete."
}

# Trap signals to call cleanup function
trap cleanup EXIT INT TERM

# Start Redis if needed
start_redis_if_needed

# Set up Python path
export PYTHONPATH="$(pwd)"

# Start the orchestrator in the background
echo "[INFO] Booting Legion orchestrator..."
echo "[INFO] Starting Orchestrator via __main__.py..." && \
python legion/orchestrator/__main__.py &
ORCHESTRATOR_PID=$!

# Check if orchestrator started successfully
sleep 2
if ! kill -0 "$ORCHESTRATOR_PID" 2>/dev/null; then
    echo "[ERROR] Orchestrator failed to start"
    exit 1
fi
echo "[INFO] Orchestrator started with PID $ORCHESTRATOR_PID"

# Start the web UI
# Ensure PORT for web UI is set, defaulting if necessary
export PORT="${PORT_ALLOCATOR_WEB_UI:-7602}"
echo "[INFO] Starting Web UI on port $PORT..."
uvicorn interface.main:app --host 0.0.0.0 --port "$PORT" --reload &
WEB_UI_PID=$!

# Check if web UI started successfully
sleep 2
if ! kill -0 "$WEB_UI_PID" 2>/dev/null; then
    echo "[ERROR] Web UI failed to start"
    exit 1
fi
echo "[INFO] Web UI started with PID $WEB_UI_PID"

# Print status
echo ""
echo "==================================="
echo "🚀 Legion Development Environment"
echo "==================================="
echo "Redis:        localhost:${LEGION_REDIS_PORT:-7600}"
echo "Orchestrator: Running (PID $ORCHESTRATOR_PID)"
echo "Web UI:       http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop all services"
echo "==================================="

# Wait for background processes to complete (until user interruption)
wait
