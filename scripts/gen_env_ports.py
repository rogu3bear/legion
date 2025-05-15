#!/usr/bin/env python3
"""
Converts a potentially nested YAML file with port definitions to .env format.

Input YAML structure can be flat or nested:
service_key1: port1
group:
  service_key2: port2
# Comments are allowed

Output .env format (keys are flattened and uppercased):
PORT_ALLOCATOR_SERVICE_KEY1=port1
PORT_ALLOCATOR_GROUP_SERVICE_KEY2=port2 # or just SERVICE_KEY2 if unique enough
"""

import sys

import yaml


def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def main():
    if len(sys.argv) != 2:
        print("Usage: python gen_env_ports.py <input_yaml_file>", file=sys.stderr)
        sys.exit(1)

    input_yaml_file = sys.argv[1]

    try:
        with open(input_yaml_file) as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Input YAML file not found: {input_yaml_file}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict):
        print(
            f"Error: YAML content must be a dictionary. Found: {type(data)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Flatten the dictionary if it's nested
    flat_data = flatten_dict(data)

    for key, value in flat_data.items():
        # Process only string keys and integer values (ports)
        if isinstance(key, str) and isinstance(value, int):
            # Create a simpler env_key, assuming the flattened key from YAML is descriptive enough
            # e.g., if YAML has services_web_ui, it becomes PORT_ALLOCATOR_SERVICES_WEB_UI
            # User instruction was PORT_ALLOCATOR_<UPPER_SNAKE>
            # The key from flat_data is already 'group_service_key' like.
            env_key_suffix = key.upper().replace("-", "_")
            env_key = f"PORT_ALLOCATOR_{env_key_suffix}"
            print(f"{env_key}={value}")
        elif isinstance(key, str) and key.strip().startswith("#"):
            # Print top-level comment lines from YAML (if safe_load preserves them, often not for comments)
            # This script mainly focuses on key-value port data.
            # A more robust comment handling would require a YAML library that preserves comments.
            print(key)  # Print the comment line
        # Other types (like string values that are comments in YAML, or non-port values) are ignored here.


if __name__ == "__main__":
    main()
