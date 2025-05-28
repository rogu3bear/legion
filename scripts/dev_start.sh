#!/usr/bin/env bash
set -e

# Docker-free Legion development startup script
echo "🚀 Starting Legion development environment (Docker-free)"

# Source port configuration
if [ -f ".env.ports" ]; then
    source .env.ports
    echo "✓ Loaded port configuration from .env.ports"
else
    echo "❌ Error: .env.ports not found"
    exit 1
fi

# Cleanup function
cleanup() {
    echo "🛑 Shutting down Legion development environment..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "✓ Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "✓ Frontend stopped"
    fi
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Check if running in dry-run mode
if [ "$1" = "--dry-run" ]; then
    echo "🧪 Dry run mode - checking services and exiting"
    DRY_RUN=true
else
    DRY_RUN=false
fi

# Detect and start Redis
echo "🔧 Checking Redis on port ${REDIS}..."
if ! redis-cli -p ${REDIS} ping >/dev/null 2>&1; then
    echo "⚠️  Redis not running on port ${REDIS}, attempting to start..."
    if command -v brew >/dev/null && brew services list | grep redis >/dev/null; then
        echo "📦 Starting Redis via brew services..."
        brew services start redis
        # Configure Redis to use our port
        redis-server --port ${REDIS} --daemonize yes
    else
        echo "🔧 Starting Redis manually on port ${REDIS}..."
        redis-server --port ${REDIS} --daemonize yes
    fi
    sleep 3
    if redis-cli -p ${REDIS} ping >/dev/null 2>&1; then
        echo "✅ Redis started successfully on port ${REDIS}"
    else
        echo "❌ Failed to start Redis"
        exit 1
    fi
else
    echo "✅ Redis already running on port ${REDIS}"
fi

if [ "$DRY_RUN" = true ]; then
    echo "✅ Dry run completed - Redis accessible, environment ready"
    exit 0
fi

# Activate Python environment
if [ -f "scripts/activate_once.sh" ]; then
    source scripts/activate_once.sh
    echo "✅ Python environment activated"
fi

# Start FastAPI backend
echo "🌐 Starting FastAPI backend on port ${LEGION_API_PORT}..."
uvicorn interface.main:app --port ${LEGION_API_PORT} --reload &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Start frontend if package.json exists
if [ -f "ui/frontend/package.json" ]; then
    echo "⚛️  Starting React frontend on port ${FRONTEND_PORT}..."
    cd ui/frontend
    npm run dev -- --port ${FRONTEND_PORT} &
    FRONTEND_PID=$!
    cd ../..
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
else
    echo "⚠️  Frontend package.json not found, skipping frontend startup"
fi

echo ""
echo "🎉 Legion development environment ready!"
echo "📡 Backend:  http://localhost:${LEGION_API_PORT}"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "🌐 Frontend: http://localhost:${FRONTEND_PORT}"
fi
echo "🗄️  Redis:    localhost:${REDIS}"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait
