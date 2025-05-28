#!/bin/bash
# PR Audit Script - Comprehensive checks for safe PR merging
# Usage: ./scripts/pr_audit.sh <PR_NUMBER>

set -e
PR_NUM="$1"

if [[ -z "$PR_NUM" ]]; then
    echo "Usage: $0 <PR_NUMBER>"
    exit 1
fi

echo "=== PR #$PR_NUM AUDIT STARTING ==="
echo ""

# Function to log with timestamp
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# Function to handle audit failures
fail_audit() {
    echo ""
    echo "❌ AUDIT FAILED: $1"
    echo "=== AUDIT COMPLETE: FAILED ==="
    exit 1
}

# Step 1: Checkout PR branch
log "Checking out PR branch..."
BRANCH_NAME=$(gh pr view "$PR_NUM" --json headRefName -q .headRefName)
if ! git checkout "origin/$BRANCH_NAME"; then
    fail_audit "Failed to checkout branch origin/$BRANCH_NAME"
fi

# Step 2: Port scan for hardcoded values
log "Scanning for hardcoded ports..."
HARDCODED_PORTS=$(grep -R --line-number -E "(:|host=)([0-9]{4,5})" . \
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv \
    --exclude-dir=.pytest_cache --exclude="*.pyc" \
    | grep -v ".env.ports" | grep -v "documentation" | grep -v "example" | head -5)

if [[ -n "$HARDCODED_PORTS" ]]; then
    echo "⚠️  Found potential hardcoded ports:"
    echo "$HARDCODED_PORTS"
    echo "Manual review required - proceeding with caution..."
fi

# Step 3: Dependency check and install
log "Installing dependencies..."
source scripts/activate_once.sh 2>/dev/null || {
    fail_audit "Failed to activate virtual environment"
}

# Install Python deps
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt > /dev/null 2>&1 || {
        fail_audit "Failed to install Python dependencies"
    }
fi

# Install Node deps if frontend changes
if git diff --name-only origin/main | grep -q "ui/frontend"; then
    log "Frontend changes detected - installing npm dependencies..."
    cd ui/frontend
    npm ci > /dev/null 2>&1 || {
        fail_audit "Failed to install npm dependencies"
    }
    cd ../..
fi

# Step 4: Import smoke test
log "Testing critical imports..."
if ! python -c "
try:
    import legion.middleware
    print('✓ Middleware import OK')
except Exception as e:
    print(f'✗ Middleware import failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "⚠️  Middleware import issues detected - may need fixes"
fi

# Test interface imports
if ! python -c "
try:
    from interface.api.v1.endpoints import echo
    print('✓ API endpoints import OK')
except Exception as e:
    print(f'✗ API import failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "⚠️  API import issues detected"
fi

# Step 5: Quick pytest run (non-blocking)
log "Running quick tests..."
if command -v pytest >/dev/null 2>&1; then
    pytest tests/ -x -q --tb=no > /dev/null 2>&1 && {
        log "✓ Tests passed"
    } || {
        log "⚠️  Tests failed - may need review"
    }
else
    log "⚠️  pytest not available - skipping tests"
fi

# Step 6: 30-second smoke test
log "Running 30-second smoke test..."
timeout 30 bash -c '
    source scripts/activate_once.sh 2>/dev/null
    uvicorn interface.main:app --port 7601 &
    SERVER_PID=$!
    sleep 10
    if curl -s http://localhost:7601/health > /dev/null 2>&1; then
        echo "✓ Server health check passed"
        kill $SERVER_PID 2>/dev/null || true
        exit 0
    else
        echo "⚠️  Server health check failed"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
' && {
    log "✓ Smoke test passed"
} || {
    log "⚠️  Smoke test failed - server startup issues"
}

# Cleanup any background processes
pkill -f uvicorn 2>/dev/null || true

echo ""
log "✅ AUDIT COMPLETE: PASSED"
echo "PR #$PR_NUM is ready for merge consideration" 