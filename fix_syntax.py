#!/usr/bin/env python3
"""
Comprehensive syntax fix script for Legion files.
Fixes missing commas in dictionaries, function calls, and parameter lists.
"""

import re
import sys
from pathlib import Path

def fix_missing_commas(content):
    """Fix missing commas in various Python constructs."""
    
    # Fix dictionary entries - look for patterns like: "key": value\n    "key2": value2
    content = re.sub(
        r'(["\'][^"\']*["\']:\s*[^,\n]+)\n(\s+["\'][^"\']*["\']:\s*)',
        r'\1,\n\2',
        content
    )
    
    # Fix function parameters - look for patterns like: param\n    param2
    content = re.sub(
        r'([a-zA-Z_][a-zA-Z0-9_]*[=\s]*[^,\n]*)\n(\s+[a-zA-Z_][a-zA-Z0-9_]*[=\s]*)',
        r'\1,\n\2',
        content
    )
    
    # Fix specific patterns found in the files
    patterns_to_fix = [
        # Dictionary entries without commas
        (r'"agent": agent_name\n(\s+)"directive":', r'"agent": agent_name,\n\1"directive":'),
        (r'"content": content\n(\s+)"directive":', r'"content": content,\n\1"directive":'),
        (r'"directive": content\n(\s+)"author":', r'"directive": content,\n\1"author":'),
        (r'"author": author or "N/A"\n(\s+)"timestamp":', r'"author": author or "N/A",\n\1"timestamp":'),
        
        # Function parameters without commas
        (r'self\n(\s+)agent_name:', r'self,\n\1agent_name:'),
        (r'agent_name: str\n(\s+)content:', r'agent_name: str,\n\1content:'),
        (r'content: str\n(\s+)author:', r'content: str,\n\1author:'),
        (r'author: Optional\[str\] = None\n(\s+)timestamp:', r'author: Optional[str] = None,\n\1timestamp:'),
        
        # Logger error calls
        (r'logger\.error\(\n(\s+)f"([^"]*?)"\n(\s+)exc_info=True\n(\s+)\)', r'logger.error(\n\1f"\2",\n\3exc_info=True,\n\4)'),
        
        # Specific fixes for known patterns
        (r'"name": agent_name\n(\s+)"config": config', r'"name": agent_name,\n\1"config": config'),
        (r'"id": message_id\n(\s+)"agent": agent_name', r'"id": message_id,\n\1"agent": agent_name'),
        (r'"original_content": content\n(\s+)"response_content":', r'"original_content": content,\n\1"response_content":'),
        (r'"response_content": response_content\n(\s+)"author":', r'"response_content": response_content,\n\1"author":'),
        
        # System status dictionary
        (r'"detail": "Orchestrator is running"\n(\s+)"pid":', r'"detail": "Orchestrator is running",\n\1"pid":'),
        (r'"pid": os\.getpid\(\)\n(\s+)"active_agents":', r'"pid": os.getpid(),\n\1"active_agents":'),
        
        # Memory stats
        (r'"status": "success"\n(\s+)"detail":', r'"status": "success",\n\1"detail":'),
        (r'"detail": "Memory system statistics \(placeholder\)"\n(\s+)"total_documents":', r'"detail": "Memory system statistics (placeholder)",\n\1"total_documents":'),
        (r'"total_documents": 0\n(\s+)"total_size_mb":', r'"total_documents": 0,\n\1"total_size_mb":'),
        (r'"total_size_mb": 0\n(\s+)"vector_db_status":', r'"total_size_mb": 0,\n\1"vector_db_status":'),
        
        # Task details
        (r'"id": str\(task_id\)\n(\s+)"status": "pending"', r'"id": str(task_id),\n\1"status": "pending"'),
        (r'"status": "pending"\n(\s+)"title": "Dummy Task"', r'"status": "pending",\n\1"title": "Dummy Task"'),
        
        # Metrics dictionary
        (r'"cpu_usage_percent": 0\.0\n(\s+)"memory_usage_mb":', r'"cpu_usage_percent": 0.0,\n\1"memory_usage_mb":'),
        (r'"memory_usage_mb": 0\.0\n(\s+)"pid":', r'"memory_usage_mb": 0.0,\n\1"pid":'),
        
        # Return statements with dictionaries
        (r'return \{\n(\s+)"([^"]+)": ([^,\n]+)\n(\s+)"([^"]+)":', r'return {\n\1"\2": \3,\n\4"\5":'),
        
        # StreamingResponse calls
        (r'StreamingResponse\(\n(\s+)([^,\n]+)\n(\s+)media_type=', r'StreamingResponse(\n\1\2,\n\3media_type='),
        (r'media_type="([^"]+)"\n(\s+)headers=', r'media_type="\1",\n\2headers='),
        
        # Exception tuples
        (r'except \(\n(\s+)ValueError\n(\s+)OSError\n(\s+)RuntimeError\n(\s+)\)', r'except (\n\1ValueError,\n\2OSError,\n\3RuntimeError,\n\4)'),
    ]
    
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    return content

def fix_file(file_path):
    """Fix syntax errors in a specific file."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return False
    
    print(f"Fixing syntax in: {file_path}")
    
    # Read the file
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply fixes
    fixed_content = fix_missing_commas(content)
    
    # Write back if changed
    if fixed_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"Applied fixes to: {file_path}")
        return True
    else:
        print(f"No changes needed for: {file_path}")
        return False

def main():
    """Main function to fix syntax in target files."""
    files_to_fix = [
        'legion/orchestrator/__init__.py',
        'interface/api/v1/endpoints/echo.py'
    ]
    
    fixed_any = False
    for file_path in files_to_fix:
        if fix_file(file_path):
            fixed_any = True
    
    if fixed_any:
        print("\nSyntax fixes applied. Please run syntax checks to verify.")
    else:
        print("\nNo syntax fixes were needed.")

if __name__ == '__main__':
    main() 