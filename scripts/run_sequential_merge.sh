#!/usr/bin/env bash
set -euo pipefail

# Sequential PR Merge Routine Wrapper
# Safely executes the Cursor Sequential PR Merge-and-Fix Routine

echo "🚀 Legion Sequential PR Merge Routine"
echo "=====================================+"

# Step 1: Environment Check
echo "🔍 Checking environment..."

# Check if we're in the right directory
if [[ ! -f "legion/__init__.py" ]] || [[ ! -d "tools" ]]; then
    echo "❌ Not in Legion repository root"
    exit 1
fi

# Check if tools are available
if [[ ! -f "tools/sequential_pr_merge.py" ]]; then
    echo "❌ Sequential merge tools not found"
    exit 1
fi

# Check git status
if ! git status --porcelain | grep -q .; then
    echo "✅ Repository is clean"
else
    echo "⚠️  Repository has uncommitted changes"
    echo "📋 Current status:"
    git status --short
    echo ""
    echo "💡 Options:"
    echo "  1. Commit changes: git add -A && git commit -m 'Pre-merge checkpoint'"
    echo "  2. Stash changes: git stash"
    echo "  3. Continue anyway (dangerous): export FORCE_MERGE=1"
    echo ""
    
    if [[ "${FORCE_MERGE:-}" != "1" ]]; then
        echo "❌ Aborting for safety. Set FORCE_MERGE=1 to override."
        exit 1
    fi
    echo "⚠️  FORCE_MERGE enabled - proceeding with uncommitted changes"
fi

# Step 2: Pre-flight checks
echo "🔧 Running pre-flight checks..."

# Port sanity check
if ! ./scripts/dev_start.sh --check-ports; then
    echo "❌ Port sanity check failed"
    exit 1
fi

# Python syntax check (basic)
if ! python -m py_compile tools/sequential_pr_merge.py; then
    echo "❌ Sequential merge script has syntax errors"
    exit 1
fi

echo "✅ Pre-flight checks passed"

# Step 3: Execute sequential merge routine
echo "🔄 Starting sequential PR merge routine..."
echo "⏰ Started at: $(date)"

# Set environment variables
export REDIS_PORT=7600
export UI_BACKEND_PORT=7601
export UI_FRONTEND_PORT=7602

# Run the main routine
if python tools/sequential_pr_merge.py; then
    echo "🎉 Sequential merge routine completed successfully!"
    exit 0
else
    echo "❌ Sequential merge routine failed"
    exit 1
fi 