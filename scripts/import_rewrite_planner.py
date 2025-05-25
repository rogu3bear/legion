#!/usr/bin/env python3
"""
ImportRewritePlanner - Scan AST and map old → new import paths.

Part of Legion Re-org Safety Blueprint Phase 2 - PR-B
"""
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

class ImportRewritePlanner(ast.NodeVisitor):
    """AST visitor to identify imports that need rewriting."""
    
    def __init__(self):
        self.imports_to_rewrite: Dict[str, str] = {}
        self.files_to_update: Set[Path] = set()
        self.import_map = {
            # Map legion.core → core (main reorganization)
            'legion.core.utils.network': 'core.utils.network',
            'legion.core.utils.indexing': 'core.utils.indexing', 
            'legion.core.utils.chroma_client': 'core.utils.chroma_client',
            'legion.core.utils': 'core.utils',
            'legion.core.logging_config': 'core.logging_config',
            'legion.core.state': 'core.state',
            'legion.core.db.models': 'core.db.models',
            'legion.core.di_container': 'core.di_container',
            'legion.core.middleware.directive_definitions': 'core.middleware.directive_definitions',
            'legion.core': 'core',
        }
    
    def visit_Import(self, node):
        """Handle 'import module' statements."""
        for alias in node.names:
            if alias.name in self.import_map:
                old_import = alias.name
                new_import = self.import_map[old_import]
                self.imports_to_rewrite[old_import] = new_import
                print(f"  Found import: {old_import} → {new_import}")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Handle 'from module import ...' statements."""
        if node.module and node.module in self.import_map:
            old_import = node.module
            new_import = self.import_map[old_import]
            self.imports_to_rewrite[old_import] = new_import
            print(f"  Found from-import: {old_import} → {new_import}")
        self.generic_visit(node)

def scan_python_files(root_path: Path) -> List[Path]:
    """Find all Python files to scan."""
    python_files = []
    for py_file in root_path.rglob("*.py"):
        # Skip certain directories
        skip_dirs = {'.venv', '__pycache__', '.git', 'node_modules'}
        if any(skip_dir in str(py_file) for skip_dir in skip_dirs):
            continue
        python_files.append(py_file)
    return python_files

def analyze_imports(file_path: Path) -> Tuple[Dict[str, str], bool]:
    """Analyze imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        planner = ImportRewritePlanner()
        planner.visit(tree)
        
        needs_update = bool(planner.imports_to_rewrite)
        return planner.imports_to_rewrite, needs_update
        
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"⚠️  Skipping {file_path}: {e}")
        return {}, False

def main():
    """Main planning function."""
    root = Path(".")
    python_files = scan_python_files(root)
    
    print(f"🔍 Scanning {len(python_files)} Python files for import rewrites...")
    
    total_rewrites = {}
    files_needing_updates = []
    
    for py_file in python_files:
        print(f"\nScanning: {py_file}")
        rewrites, needs_update = analyze_imports(py_file)
        
        if needs_update:
            files_needing_updates.append(py_file)
            total_rewrites.update(rewrites)
    
    print(f"\n📊 Import Rewrite Plan:")
    print(f"Files to update: {len(files_needing_updates)}")
    print(f"Import mappings found: {len(total_rewrites)}")
    
    if total_rewrites:
        print(f"\n🔄 Mappings:")
        for old, new in total_rewrites.items():
            print(f"  {old} → {new}")
    
    if files_needing_updates:
        print(f"\n📝 Files needing updates:")
        for file_path in files_needing_updates:
            print(f"  - {file_path}")
    
    return len(files_needing_updates), len(total_rewrites)

if __name__ == "__main__":
    files_count, mappings_count = main()
    print(f"\n✅ Planning complete: {files_count} files, {mappings_count} mappings") 