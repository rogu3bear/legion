#!/bin/bash
cd "$(dirname "$0")/.."
source .venv/bin/activate
cd interface
uvicorn main:app --reload --port 8000 