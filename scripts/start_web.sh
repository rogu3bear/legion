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

# Set default PORT if not defined, use 8081 as suggested
: ${PORT:=8081}

# Port selection with retry
MAX_RETRIES=5
RETRY_DELAY=5
for i in $(seq 1 $MAX_RETRIES); do
    if lsof -i :$PORT > /dev/null; then
        log_msg "WARNING: Port $PORT in use. Retrying in $RETRY_DELAY seconds... (Attempt $i)"
        if [ $i -eq $MAX_RETRIES ]; then
            log_msg "ERROR: Port $PORT still in use after $MAX_RETRIES attempts. Exiting."
            exit 1
        fi
        sleep $RETRY_DELAY
    else
        break
    fi
done
log_msg "INFO: Port $PORT is free. Proceeding."

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
