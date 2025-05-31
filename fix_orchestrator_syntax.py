#!/usr/bin/env python3
"""
Comprehensive syntax fix script for legion/orchestrator/__init__.py
Fixes missing commas in function calls, dictionaries, and parameter lists.
"""
import re
import sys
from pathlib import Path

def fix_missing_commas(file_path):
    """Fix common missing comma patterns in the orchestrator file."""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern 1: Fix missing commas in logger.error calls before exc_info
    content = re.sub(
        r'(logger\.error\(\s*[^)]+)\n(\s+)(exc_info=)',
        r'\1,\n\2\3',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 2: Fix missing commas in function/method parameter lists
    content = re.sub(
        r'(\w+\s*=\s*[^,\n]+)\n(\s+)(\w+\s*[:=])',
        r'\1,\n\2\3',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 3: Fix missing commas in dictionary definitions
    content = re.sub(
        r'("[^"]+"\s*:\s*[^,\n}]+)\n(\s+)("[^"]+"\s*:)',
        r'\1,\n\2\3',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 4: Fix missing commas in list definitions  
    content = re.sub(
        r'(\{[^}]*)\n(\s+)("[^"]+"\s*:)',
        r'\1,\n\2\3',
        content,
        flags=re.MULTILINE
    )
    
    # Pattern 5: Fix specific known missing comma patterns
    patterns = [
        # agent_memory.log_interaction call
        (r'(prompt=prompt)\n(\s+)(response=)', r'\1,\n\2\3'),
        (r'(response=response)\n(\s+)(context=)', r'\1,\n\2\3'),
        
        # messages list
        (r'(\{\s*)\n(\s+)("role":\s*"system")\n(\s+)("content":)', r'\1\n\2\3,\n\4\5'),
        
        # notify_agent call
        (r'(mentioned)\n(\s+)(f"Mentioned)', r'\1,\n\2\3'),
        
        # render_feed_item calls
        (r'(payload\.get\([^)]+\))\n(\s+)(payload\.get\([^)]+\))', r'\1,\n\2\3'),
        
        # Task constructor calls
        (r'(id=str\([^)]+\))\n(\s+)(agent=)', r'\1,\n\2\3'),
        (r'(agent=[^,\n]+)\n(\s+)(payload=)', r'\1,\n\2\3'),
        
        # Dictionary value assignments
        (r'("status":\s*"[^"]+)\n(\s+)("detail":)', r'\1,\n\2\3'),
        (r'("type":\s*"[^"]+)\n(\s+)("agent":)', r'\1,\n\2\3'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Write back the fixed content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Applied comprehensive syntax fixes to {file_path}")

if __name__ == "__main__":
    orchestrator_file = Path("legion/orchestrator/__init__.py")
    
    if not orchestrator_file.exists():
        print(f"Error: {orchestrator_file} not found")
        sys.exit(1)
    
    print("Applying comprehensive syntax fixes...")
    fix_missing_commas(orchestrator_file)
    print("Syntax fixes complete!") 