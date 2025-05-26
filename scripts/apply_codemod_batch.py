#!/usr/bin/env python3
"""
ApplyCodemodBatch - Execute import rewrite set with logging.

Part of Legion Re-org Safety Blueprint Phase 2 - PR-B
"""
import re
from pathlib import Path
from typing import Dict, List


class CodemodBatch:
    """Apply import rewrites to files."""

    def __init__(self):
        self.import_map = {
            "legion.core.logging_config": "core.logging_config",
            "legion.core.state": "core.state",
            "legion.core.db.models": "core.db.models",
            "legion.core.middleware.directive_definitions": "core.middleware.directive_definitions",
            "legion.core.di_container": "core.di_container",
        }
        self.files_updated = []
        self.total_replacements = 0

    def rewrite_file(self, file_path: Path) -> int:
        """Rewrite imports in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            replacements_made = 0

            # Apply each mapping
            for old_import, new_import in self.import_map.items():
                # Handle "from module import ..." patterns
                pattern_from = rf"from {re.escape(old_import)}\b"
                replacement_from = f"from {new_import}"

                content, count_from = re.subn(pattern_from, replacement_from, content)
                replacements_made += count_from

                # Handle "import module" patterns
                pattern_import = rf"\bimport {re.escape(old_import)}\b"
                replacement_import = f"import {new_import}"

                content, count_import = re.subn(
                    pattern_import, replacement_import, content
                )
                replacements_made += count_import

                if count_from > 0 or count_import > 0:
                    print(
                        f"    {old_import} → {new_import} ({count_from + count_import} replacements)"
                    )

            # Write back if changes were made
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.files_updated.append(file_path)
                self.total_replacements += replacements_made
                return replacements_made

            return 0

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return 0

    def apply_to_files(self, file_paths: List[Path]) -> Dict[str, int]:
        """Apply codemods to a list of files."""
        results = {}

        print(f"🔄 Applying codemods to {len(file_paths)} files...")

        for file_path in file_paths:
            print(f"\nProcessing: {file_path}")
            replacements = self.rewrite_file(file_path)
            results[str(file_path)] = replacements

            if replacements > 0:
                print(f"  ✅ {replacements} replacements made")
            else:
                print("  ⏭️  No changes needed")

        return results


def main():
    """Main codemod application function."""
    # Files identified by the planner
    target_files = [
        "interface/main.py",
        "scripts/test_redis_snapshot.py",
        "memory/db/models.py",
        "integration/discord/bot.py",
        "tests/core/test_middleware_directive.py",
        "tests/integration/test_orchestrator_bench.py",
        "tests/integration/conftest.py",
        "tests/integration/test_orchestrator_errors.py",
        "tests/integration/test_orchestrator_dispatch.py",
        "legion/core/di_container.py",
        "legion/agents/base.py",
        "legion/orchestrator/__init__.py",
        "legion/core/db/migrations/0002_create_tasks.py",
    ]

    # Convert to Path objects and filter existing files
    file_paths = []
    for file_str in target_files:
        file_path = Path(file_str)
        if file_path.exists():
            file_paths.append(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")

    codemod = CodemodBatch()
    codemod.apply_to_files(file_paths)

    print("\n📊 Codemod Batch Results:")
    print(f"Files processed: {len(file_paths)}")
    print(f"Files updated: {len(codemod.files_updated)}")
    print(f"Total replacements: {codemod.total_replacements}")

    if codemod.files_updated:
        print("\n📝 Updated files:")
        for file_path in codemod.files_updated:
            print(f"  - {file_path}")

    return len(codemod.files_updated), codemod.total_replacements


if __name__ == "__main__":
    files_updated, replacements = main()
    print(
        f"\n✅ Codemod complete: {files_updated} files updated, {replacements} replacements"
    )
