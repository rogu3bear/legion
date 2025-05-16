#!/usr/bin/env bash

set -euo pipefail

# Function for timestamped logging
function log_msg {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Load environment variables
if [ -f .env ]; then
    set -a; source .env; set +a
    log_msg "INFO: Loaded environment variables from .env"
else
    log_msg "ERROR: .env file not found. Exiting."
    exit 1
fi

# Create and activate virtual environment, install dependencies if needed
if [ ! -d .venv ]; then
    log_msg "INFO: Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    log_msg "INFO: Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Ensure PORT is set by environment
if [ -z "${PORT:-}" ]; then
    log_msg "ERROR: PORT is not set. Please configure it in your environment."
    exit 1
fi

# Set default environment variables with better security practices
: ${SQLALCHEMY_DATABASE_URI:="sqlite:///memory/db/legion.db"}
: ${SECRET_KEY:="change-this-in-production"}
: ${ALLOWED_HOSTS:="http://localhost:$PORT,http://localhost"}

# Validate required environment variables for web interface
required_vars=("SQLALCHEMY_DATABASE_URI" "SECRET_KEY" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        log_msg "ERROR: $var is not set. Please configure it."
        exit 1
    fi
done

# Run migrations
log_msg "INFO: Running Alembic migrations..."
if ! alembic upgrade head; then
    log_msg "ERROR: Alembic migrations failed."
    exit 1
fi

# Start Legion Orchestrator in background
log_msg "INFO: Starting Legion Orchestrator..."
nohup python legion/orchestrator.py > orchestrator.log 2>&1 &

# Start web interface
log_msg "INFO: Starting web interface on port $PORT..."
uvicorn interface.main:app --host 0.0.0.0 --port $PORT --reload
