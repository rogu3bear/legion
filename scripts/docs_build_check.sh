#!/usr/bin/env bash
set -e
mkdocs build -q || exit 1
python -m markdown_link_check docs/ --quiet
