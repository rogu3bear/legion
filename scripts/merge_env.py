import sys
from collections import OrderedDict
from dotenv import dotenv_values, set_key

if len(sys.argv) != 3:
    print("Usage: python merge_env.py .env .env.example")
    sys.exit(1)

current_path, template_path = sys.argv[1], sys.argv[2]
current = dotenv_values(current_path)
template = dotenv_values(template_path)

# Read lines for comment and order preservation
with open(current_path) as f:
    current_lines = f.readlines()
with open(template_path) as f:
    template_lines = f.readlines()

# Build ordered set of keys from both files
ordered_keys = []
seen = set()
for line in current_lines + template_lines:
    if line.strip().startswith("#") or not line.strip():
        continue
    if "=" in line:
        k = line.split("=", 1)[0].strip()
        if k not in seen:
            ordered_keys.append(k)
            seen.add(k)

# Merge values, preferring current
merged = OrderedDict()
for k in ordered_keys:
    if k in current:
        merged[k] = current[k]
    elif k in template:
        merged[k] = template[k]
    else:
        merged[k] = ""

# Write merged .env, preserving comments and order
with open(current_path, "w") as out:
    # Write comments and blank lines from template first
    for line in template_lines:
        if line.strip().startswith("#") or not line.strip():
            out.write(line)
    # Write merged keys
    for k in ordered_keys:
        out.write(f"{k}={merged[k]}\n")

print("Merged missing keys into .env") 