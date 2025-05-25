#!/usr/bin/env python3
"""Pre-commit hook: prevent non-Markdown files in docs/ directory."""
import sys
import os
from pathlib import Path

def check_docs_file_types():
    """Check that only markdown files are in docs/ directory."""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        return True

    violations = []
    allowed_extensions = {'.md', '.markdown', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.puml', '.plantuml'}

    for file_path in docs_dir.rglob('*'):
        if file_path.is_file():
            if file_path.suffix.lower() not in allowed_extensions:
                violations.append(str(file_path))

    if violations:
        print("❌ DOCS FILE TYPE VIOLATION:")
        print("Only Markdown files (.md, .markdown) are allowed in docs/")
        print("\nViolating files:")
        for violation in violations:
            print(f"  - {violation}")
        print("\nMove these files outside docs/ or convert to Markdown.")
        return False

    return True

if __name__ == "__main__":
    if not check_docs_file_types():
        sys.exit(1)
    print("✅ Docs file type check passed")
