#!/usr/bin/env python3
"""
Auto-resolve merge conflicts for Legion repository.
Attempts to resolve common conflicts automatically while preserving critical structure.
"""

import os
import sys
import subprocess
import re
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def get_conflicted_files():
    """Get list of files with merge conflicts."""
    code, stdout, _ = run_command("git diff --name-only --diff-filter=U")
    if code == 0:
        return [f.strip() for f in stdout.split('\n') if f.strip()]
    return []


def resolve_simple_conflicts(file_path):
    """
    Resolve simple conflicts by applying these rules:
    1. For imports: take both versions (deduplicate)
    2. For version conflicts: take the higher version
    3. For documentation: prefer incoming changes
    4. For structural conflicts: manual review needed
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has conflict markers
    if not ('<<<<<<< HEAD' in content and '>>>>>>> ' in content):
        return False, "No conflicts found"
    
    original_content = content
    resolved = False
    
    # Pattern to match conflict blocks
    conflict_pattern = re.compile(
        r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> ([^\n]+)',
        re.DOTALL
    )
    
    def resolve_conflict_block(match):
        nonlocal resolved
        head_content = match.group(1).strip()
        incoming_content = match.group(2).strip()
        branch_name = match.group(3)
        
        # Rule 1: Import conflicts - merge both
        if (head_content.startswith('import ') or head_content.startswith('from ')) and \
           (incoming_content.startswith('import ') or incoming_content.startswith('from ')):
            head_imports = set(line.strip() for line in head_content.split('\n') if line.strip())
            incoming_imports = set(line.strip() for line in incoming_content.split('\n') if line.strip())
            all_imports = sorted(head_imports | incoming_imports)
            resolved = True
            return '\n'.join(all_imports)
        
        # Rule 2: Version conflicts - take higher version
        version_pattern = r'version\s*[=:]\s*["\']([0-9.]+)["\']'
        head_version_match = re.search(version_pattern, head_content, re.IGNORECASE)
        incoming_version_match = re.search(version_pattern, incoming_content, re.IGNORECASE)
        
        if head_version_match and incoming_version_match:
            head_version = head_version_match.group(1)
            incoming_version = incoming_version_match.group(1)
            
            def version_tuple(v):
                return tuple(map(int, (v.split('.'))))
            
            try:
                if version_tuple(incoming_version) > version_tuple(head_version):
                    resolved = True
                    return incoming_content
                else:
                    resolved = True
                    return head_content
            except ValueError:
                pass
        
        # Rule 3: Documentation files - prefer incoming
        if file_path.endswith(('.md', '.rst', '.txt')):
            resolved = True
            return incoming_content
        
        # Rule 4: Empty content resolution
        if not head_content and incoming_content:
            resolved = True
            return incoming_content
        elif head_content and not incoming_content:
            resolved = True
            return head_content
        
        # Rule 5: Identical content after whitespace normalization
        if head_content.strip() == incoming_content.strip():
            resolved = True
            return head_content
        
        # Cannot auto-resolve - leave for manual resolution
        return match.group(0)
    
    # Apply conflict resolution
    new_content = conflict_pattern.sub(resolve_conflict_block, content)
    
    if resolved and new_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, "Conflicts resolved automatically"
    elif new_content == original_content and '<<<<<<< HEAD' in content:
        return False, "Manual resolution required"
    else:
        return False, "No resolvable conflicts"


def main():
    """Main auto-conflict resolution routine."""
    print("🔧 Auto-resolving merge conflicts...")
    
    conflicted_files = get_conflicted_files()
    if not conflicted_files:
        print("✅ No conflicted files found")
        return 0
    
    print(f"📁 Found {len(conflicted_files)} conflicted files:")
    for file_path in conflicted_files:
        print(f"  - {file_path}")
    
    resolved_count = 0
    manual_review_files = []
    
    for file_path in conflicted_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        success, message = resolve_simple_conflicts(file_path)
        if success:
            print(f"✅ {file_path}: {message}")
            resolved_count += 1
        else:
            print(f"⚠️  {file_path}: {message}")
            manual_review_files.append(file_path)
    
    print(f"\n📊 Resolution Summary:")
    print(f"  - Automatically resolved: {resolved_count}")
    print(f"  - Manual review needed: {len(manual_review_files)}")
    
    if manual_review_files:
        print(f"\n🔍 Files requiring manual review:")
        for file_path in manual_review_files:
            print(f"  - {file_path}")
        return 1
    
    print("✅ All conflicts resolved automatically")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 