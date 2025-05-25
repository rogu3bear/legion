#!/usr/bin/env python3
"""Simple documentation linter."""
import os
import re
import subprocess
from pathlib import Path

DEPRECATED = [
    "schema.sql",
    "localhost:8000",
    "task_log.jsonl",
]

# Exclude common non-doc directories
EXCLUDE_DIRS = {
    ".venv", ".mypy_cache", ".git", "node_modules", "__pycache__",
    ".pytest_cache", "dist", "build", ".tox", "venv"
}

def scan_file(path: Path) -> None:
    """Scan file for deprecated terms."""
    try:
        text = path.read_text(errors="ignore")
        for term in DEPRECATED:
            if term in text:
                print(f"{path}: deprecated term '{term}' found")
    except Exception as e:
        print(f"{path}: error reading file - {e}")


def check_links() -> None:
    """Check for broken links in documentation using lychee if available."""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("docs/ directory not found, skipping link check")
        return

    try:
        # Try to run lychee for link checking
        result = subprocess.run(
            ["lychee", "--offline", "docs"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✓ Link check passed")
        else:
            print("⚠ Link check found issues:")
            print(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("lychee not available, skipping link check")


def main() -> None:
    """Main linter function."""
    repo = Path.cwd()

    # Focus primarily on docs directory
    targets = []

    # Add all markdown files in docs/
    docs_dir = repo / "docs"
    if docs_dir.exists():
        targets.extend(docs_dir.rglob("*.md"))

    # Add root-level documentation files
    for pattern in ["*.md", "*.txt"]:
        targets.extend(repo.glob(pattern))

    # Scan files for deprecated terms
    for path in targets:
        # Skip excluded directories
        if any(exclude in str(path) for exclude in EXCLUDE_DIRS):
            continue
        scan_file(path)

    # Check for broken links
    check_links()

    print(f"Scanned {len(targets)} documentation files")


if __name__ == "__main__":
    main()
