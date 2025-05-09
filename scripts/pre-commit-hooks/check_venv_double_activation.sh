#!/usr/bin/env bash
# Pre-commit hook to check for double virtual environment activations
# This can be symlinked to .git/hooks/pre-commit

# Check if PS1 has multiple venv indicators
if [[ "$PS1" == *"(venv) (venv)"* ]] || [[ "$PS1" == *"(.venv) (.venv)"* ]] || 
   [[ "$PS1" == *"((.venv"* ]] || [[ "$(echo "$PS1" | grep -o "venv" | wc -l)" -gt 1 ]]; then
    echo "ERROR: Double virtual environment activation detected!"
    echo "You have activated the virtual environment multiple times."
    echo "To fix:"
    echo "  1. Run 'deactivate' until you no longer see a virtual environment prefix"
    echo "  2. Use 'source scripts/activate_once.sh' to safely activate once"
    exit 1
fi

# Check for duplicate entries in PATH
VENV_PATH_COUNT=$(echo "$PATH" | tr ':' '\n' | grep -c "\.venv/bin")
if [[ "$VENV_PATH_COUNT" -gt 1 ]]; then
    echo "WARNING: Multiple virtual environment entries detected in PATH!"
    echo "This could cause unexpected behavior."
    echo "To fix: Deactivate completely and use 'source scripts/activate_once.sh'."
    exit 1
fi

# All checks passed
exit 0
