#!/usr/bin/env python3
import re

# Read the file
with open('legion/orchestrator/__init__.py', 'r') as f:
    content = f.read()

# Fix over-applied commas
fixes = [
    (r'except Exception:,', 'except Exception:'),
    (r':\s*,\n', ':\n'),
    (r'import ([^,\n]+),\n(?!\s)', r'import \1\n'),
    (r'as ([^,\n]+),\n(?!\s)', r'as \1\n'),
]

for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Write back
with open('legion/orchestrator/__init__.py', 'w') as f:
    f.write(content)

print('Fixed over-applied commas') 