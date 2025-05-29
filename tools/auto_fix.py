#!/usr/bin/env python3
"""
Auto-fix tool for Legion repository.
Automatically resolves common linting issues, import problems, and syntax errors.
"""

import os
import sys
import subprocess
import re
import ast
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


def run_command(cmd: str, check: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def get_python_files() -> List[Path]:
    """Get all Python files in the repository."""
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories, __pycache__, and .venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    return python_files


def fix_import_order(file_path: Path) -> bool:
    """Fix import order using isort-like logic."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        imports = []
        from_imports = []
        other_lines = []
        in_import_section = True
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') and in_import_section:
                imports.append(line)
            elif stripped.startswith('from ') and in_import_section:
                from_imports.append(line)
            elif stripped == '' and in_import_section:
                # Keep empty lines in import section
                continue
            else:
                if stripped and not stripped.startswith('#'):
                    in_import_section = False
                other_lines.append(line)
        
        if imports or from_imports:
            # Sort imports
            imports.sort()
            from_imports.sort()
            
            # Rebuild content
            new_lines = []
            if imports:
                new_lines.extend(imports)
            if from_imports:
                if imports:
                    new_lines.append('')
                new_lines.extend(from_imports)
            if new_lines and other_lines:
                new_lines.append('')
                new_lines.append('')
            new_lines.extend(other_lines)
            
            new_content = '\n'.join(new_lines)
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
    except Exception as e:
        print(f"⚠️  Error fixing imports in {file_path}: {e}")
    return False


def fix_syntax_errors(file_path: Path) -> bool:
    """Fix common syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix common issues
        # 1. Remove trailing commas in inappropriate places
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # 2. Fix double quotes in f-strings
        content = re.sub(r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"', content)
        
        # 3. Fix missing commas in lists/tuples
        content = re.sub(r'(\w+)(\s+)(\w+\s*[,\]])', r'\1,\2\3', content)
        
        # Check if the content is now syntactically valid
        try:
            ast.parse(content)
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        except SyntaxError:
            # Revert if we broke something
            pass
            
    except Exception as e:
        print(f"⚠️  Error fixing syntax in {file_path}: {e}")
    return False


def fix_linting_issues() -> bool:
    """Fix common linting issues using automated tools."""
    fixed = False
    
    # Try to use autopep8 if available
    code, stdout, stderr = run_command("which autopep8", check=False)
    if code == 0:
        print("🔧 Running autopep8...")
        code, stdout, stderr = run_command("autopep8 --in-place --recursive --max-line-length=100 .", check=False)
        if code == 0:
            fixed = True
            print("✅ autopep8 fixes applied")
        else:
            print(f"⚠️  autopep8 issues: {stderr}")
    
    # Try to use black if available
    code, stdout, stderr = run_command("which black", check=False)
    if code == 0:
        print("🔧 Running black...")
        code, stdout, stderr = run_command("black --line-length 100 .", check=False)
        if code == 0:
            fixed = True
            print("✅ black formatting applied")
        else:
            print(f"⚠️  black issues: {stderr}")
    
    return fixed


def fix_file_level_issues(file_path: Path) -> bool:
    """Fix file-level issues like imports and syntax."""
    fixed = False
    
    if fix_import_order(file_path):
        print(f"✅ Fixed imports in {file_path}")
        fixed = True
    
    if fix_syntax_errors(file_path):
        print(f"✅ Fixed syntax errors in {file_path}")
        fixed = True
    
    return fixed


def run_assurance_scan(min_score: float = 0.85) -> bool:
    """Run assurance scan if available."""
    # Check if assurance scan module exists
    code, stdout, stderr = run_command("python -c 'import legion.core.assurance'", check=False)
    if code != 0:
        print("⚠️  Assurance scan module not found, skipping...")
        return True
    
    code, stdout, stderr = run_command(f"python -m tools.assurance_scan --min {min_score}", check=False)
    if code == 0:
        print("✅ Assurance scan passed")
        return True
    else:
        print(f"❌ Assurance scan failed: {stderr}")
        return False


def run_type_checking() -> bool:
    """Run type checking with pyright."""
    code, stdout, stderr = run_command("which pyright", check=False)
    if code != 0:
        print("⚠️  pyright not found, skipping type checking...")
        return True
    
    code, stdout, stderr = run_command("pyright --project .", check=False)
    if code == 0:
        print("✅ Type checking passed")
        return True
    else:
        print(f"❌ Type checking failed: {stderr}")
        return False


def main():
    """Main auto-fix routine."""
    parser = argparse.ArgumentParser(description="Auto-fix Legion repository issues")
    parser.add_argument("--ci", action="store_true", help="Run in CI mode (more aggressive fixes)")
    parser.add_argument("--min-assurance", type=float, default=0.85, help="Minimum assurance score")
    args = parser.parse_args()
    
    print("🔧 Starting auto-fix routine...")
    
    success = True
    
    # Step 1: Fix linting issues with automated tools
    if args.ci:
        print("\n📋 Step 1: Running automated linting fixes...")
        if fix_linting_issues():
            print("✅ Automated linting fixes applied")
        else:
            print("⚠️  No automated linting tools available")
    
    # Step 2: Fix file-level issues
    print("\n📋 Step 2: Fixing file-level issues...")
    python_files = get_python_files()
    fixed_files = 0
    
    for file_path in python_files:
        if fix_file_level_issues(file_path):
            fixed_files += 1
    
    if fixed_files > 0:
        print(f"✅ Fixed issues in {fixed_files} files")
    else:
        print("✅ No file-level fixes needed")
    
    # Step 3: Run port-sanity check
    print("\n📋 Step 3: Running port-sanity check...")
    code, stdout, stderr = run_command("./scripts/dev_start.sh --check-ports", check=False)
    if code != 0:
        # Try to run the port check function directly
        print("⚠️  Port check with --check-ports flag failed, trying alternative...")
        code, stdout, stderr = run_command("python check_ports.py", check=False)
        if code == 0:
            print("✅ Port configuration validated")
        else:
            print(f"⚠️  Port validation issues: {stderr}")
            success = False
    else:
        print("✅ Port-sanity check passed")
    
    # Step 4: Run assurance scan
    print(f"\n📋 Step 4: Running assurance scan (min score: {args.min_assurance})...")
    if not run_assurance_scan(args.min_assurance):
        success = False
    
    # Step 5: Run type checking
    print("\n📋 Step 5: Running type checking...")
    if not run_type_checking():
        success = False
    
    if success:
        print("\n✅ All auto-fixes completed successfully!")
        return 0
    else:
        print("\n❌ Some issues remain that require manual intervention")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 