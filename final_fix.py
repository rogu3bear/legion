#!/usr/bin/env python3
import re

with open('legion/orchestrator/__init__.py', 'r') as f:
    content = f.read()

# Fix all remaining logger.error calls with missing commas
content = re.sub(
    r'(logger\.error\(\s*\n\s*f\"[^\"]*\{[^}]*\}[^\"]*\")\s*\n(\s*exc_info=)',
    r'\1,\n\2',
    content,
    flags=re.MULTILINE
)

# Fix specific remaining issues
fixes = [
    # Fix any remaining f-string issues in logger calls
    (r'f"([^"]*\{[^}]*\}[^"]*)"(\s*\n\s*exc_info=)', r'f"\1",\2'),
    
    # Fix any remaining dictionary entries
    (r'"(\w+)": ([^,\n]+)\n(\s+)"(\w+)":', r'"\1": \2,\n\3"\4":'),
    
    # Fix any remaining function parameters
    (r'(\w+)=([^,\n]+)\n(\s+)(\w+)=', r'\1=\2,\n\3\4='),
    
    # Fix specific patterns that might remain
    (r'prompt=prompt\s*\n\s*response=response', r'prompt=prompt,\n                        response=response'),
    (r'response=response\s*\n\s*context=context', r'response=response,\n                        context=context'),
]

for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

with open('legion/orchestrator/__init__.py', 'w') as f:
    f.write(content)

print('Applied final comprehensive syntax fixes') 