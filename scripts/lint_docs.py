#!/usr/bin/env python3
"""Simple documentation linter."""
import os
import re
from pathlib import Path

DEPRECATED = [
    "schema.sql",
    "localhost:8000",
    "task_log.jsonl",
]

ALLOWED_TXT_DIRS = {"docs", "tests", "scripts", "artifacts"}
ALLOWED_JSON_DIRS = {"docs", "memory", "generated", "schemas", "interface", "ui", "legion"}


def scan_file(path: Path) -> None:
    text = path.read_text(errors="ignore")
    for term in DEPRECATED:
        if term in text:
            print(f"{path}: deprecated term '{term}' found")


def warn_misplaced(repo: Path, path: Path) -> None:
    rel = path.relative_to(repo)
    parts = rel.parts
    if path.suffix == ".txt" and parts and parts[0] not in ALLOWED_TXT_DIRS:
        print(f"{rel}: unexpected .txt file")
    if path.suffix == ".json" and parts and parts[0] not in ALLOWED_JSON_DIRS:
        print(f"{rel}: unexpected .json file")


def main() -> None:
    repo = Path.cwd()
    for root, _, files in os.walk(repo):
        for name in files:
            p = Path(root) / name
            if p.suffix in {".md", ".txt", ".json"}:
                scan_file(p)
                warn_misplaced(repo, p)


if __name__ == "__main__":
    main()
