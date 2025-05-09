#!/usr/bin/env bash
# Development environment setup script
# Handles virtual environment and dependency installation

set -e  # Exit on error

# Get the absolute path to the project root
if [[ -n "${BASH_SOURCE[0]}" ]]; then
    # Running in bash
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
else
    # Fallback to current directory (may be running in zsh or other shell)
    PROJECT_ROOT="$(pwd)"
fi

# Special case handling for Legion project
if [[ "$(basename "$PROJECT_ROOT")" != "Legion" && -d "$(pwd)/Legion" ]]; then
    PROJECT_ROOT="$(pwd)/Legion"
elif [[ "$(basename "$PROJECT_ROOT")" != "Legion" && "$(basename "$(pwd)")" == "Legion" ]]; then
    PROJECT_ROOT="$(pwd)"
fi

cd "$PROJECT_ROOT"
echo "Project root: $PROJECT_ROOT"

# Check if Python is installed
if ! command -v python &>/dev/null; then
    echo "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [[ ! -d ".venv" ]]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Source our safe activation script
source scripts/activate_once.sh

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -U pip
pip install -r requirements.txt

# Generate dependencies lock file using pip-tools if specified
if [[ "$1" == "--lock" || "$1" == "-l" ]]; then
    echo "Generating deterministic dependencies lock file..."
    pip install pip-tools
    pip-compile --resolver=backtracking -o requirements-lock.txt requirements.txt
    echo "Created requirements-lock.txt with exact dependency versions."
fi

# Inform user of next steps
echo "Development environment setup complete!"
echo "Use 'source scripts/activate_once.sh' to activate the virtual environment in the future."
echo "Run 'mypy legion/' and 'flake8 legion/' to check for validation issues."
echo ""
echo "To create a deterministic lock file, run: ./scripts/dev_setup.sh --lock"
echo "To deactivate the virtual environment, run: deactivate" 