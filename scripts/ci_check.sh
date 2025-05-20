#!/usr/bin/env bash
# CI sanity: compile, test, smoke

# Add stub packages to PYTHONPATH
export PYTHONPATH="tests/stubs:$PYTHONPATH"

python -m compileall . || exit 1
python -m unittest discover -v || exit 1
python scripts/smoke_placeholder.py || exit 1
