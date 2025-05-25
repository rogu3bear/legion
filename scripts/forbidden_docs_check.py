#!/usr/bin/env python3
"""CI script: prevent .md files outside docs/ directory."""
import sys
from pathlib import Path

def check_forbidden_docs():
    """Check for .md files outside docs/ directory."""
    repo_root = Path(".")
    docs_dir = repo_root / "docs"

    violations = []
    allowed_root_files = {
        'README.md', 'CONTRIBUTING.md', 'CHANGELOG.md', 'changelog.md',
        'LICENSE.md', 'SECURITY.md', 'CODE_OF_CONDUCT.md'
    }

    # Find all .md files
    for md_file in repo_root.rglob("*.md"):
        # Skip files in docs/ directory
        if docs_dir in md_file.parents or md_file.parent == docs_dir:
            continue

        # Skip allowed root-level files
        if md_file.parent == repo_root and md_file.name in allowed_root_files:
            continue

        # Skip hidden directories and node_modules
        if any(part.startswith('.') or part == 'node_modules' for part in md_file.parts):
            continue

        # Skip specific directories
        skip_dirs = {'ui', 'artifacts', 'legion/prompts', 'research'}
        if any(skip_dir in str(md_file) for skip_dir in skip_dirs):
            continue
            
        # Allow README.md in skills subdirectories
        if md_file.name == 'README.md' and 'skills/' in str(md_file):
            continue

        violations.append(str(md_file))

    if violations:
        print("❌ FORBIDDEN DOCS VIOLATION:")
        print("Markdown files should be in docs/ directory only")
        print("(except allowed root files: README.md, CONTRIBUTING.md, etc.)")
        print("\nViolating files:")
        for violation in violations:
            print(f"  - {violation}")
        print("\nMove these files to docs/ directory.")
        return False

    return True

if __name__ == "__main__":
    if not check_forbidden_docs():
        sys.exit(1)
    print("✅ Forbidden docs check passed")
