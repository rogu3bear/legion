#!/usr/bin/env python3
"""
Converts a potentially nested YAML file with port definitions to .env format.

Input YAML structure can be flat or nested:
service_key1: port1
group:
  service_key2: port2
# Comments are allowed

Output .env format (keys are flattened, uppercased, and prefixes removed):
PORT_ALLOCATOR_SERVICE_KEY1=port1
# becomes PORT_ALLOCATOR_KEY1 after stripping common prefixes
"""

import sys

import yaml

# Prefixes to remove from the keys
PREFIXES_TO_STRIP = [
    "services_",
    "agents_",
    "core_services_",
    "middleware_",
    "orchestrator_", # if orchestrator_zmq_rep_port should become zmq_rep_port
]

def strip_prefixes(key_str):
    """Strips defined prefixes from the start of a key string."""
    original_key = key_str
    for prefix in PREFIXES_TO_STRIP:
        if key_str.startswith(prefix):
            key_str = key_str[len(prefix):]
    # Special handling for zmq parts of orchestrator if needed, could be more generic
    if original_key.startswith("orchestrator_") and "zmq" in key_str:
         # e.g., orchestrator_zmq_rep_port -> zmq_rep_port
         pass # Already handled if orchestrator_ is in PREFIXES_TO_STRIP
    return key_str

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            # Strip prefixes from the final key component before uppercasing
            # Or, strip from the fully formed new_key if that's intended
            # Current logic: flatten, then process the full key
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
        print("Error: Root of YAML file must be a dictionary.", file=sys.stderr)
        sys.exit(1)

    flattened_data = flatten_dict(data)

    output_lines = []
    for key, value in flattened_data.items():
        # Process the key: lowercase, strip prefixes, then uppercase
        processed_key = key.lower()
        # Example: 'services_web_ui' -> 'web_ui'
        # Example: 'core_services_chroma' -> 'chroma'

        # More robust prefix stripping from the full key
        temp_key = processed_key
        for prefix in PREFIXES_TO_STRIP:
            if temp_key.startswith(prefix):
                temp_key = temp_key[len(prefix):]

        # If after stripping all defined prefixes, a key part still looks like a prefix
        # (e.g. services_web_ui -> web_ui rather than just ui)
        # This might need more sophisticated logic if keys are like 'services_core_web_ui'
        # For now, simple prefix removal on the flattened key.

        for _part in temp_key.split('_'):
             # This logic might be too aggressive or not match the desired outcome.
             # The goal is to get `PORT_ALLOCATOR_CHROMA` from `PORT_ALLOCATOR_CORE_SERVICES_CHROMA`
             # or `PORT_ALLOCATOR_WEB_UI` from `PORT_ALLOCATOR_SERVICES_WEB_UI`
             # A simpler approach is to just strip the longest matching prefix.
             pass # The stripping logic below is preferred

        # Simpler stripping: take the full flattened key, lowercase it, strip known prefixes
        # and then make it uppercase.
        key_to_process = key.lower()
        stripped_key = key_to_process
        for prefix in PREFIXES_TO_STRIP:
            if stripped_key.startswith(prefix):
                stripped_key = stripped_key[len(prefix):]

        # Further refinement for keys like 'orchestrator_zmq_rep_port' -> 'zmq_rep_port'
        # This is implicitly handled if 'orchestrator_' is in PREFIXES_TO_STRIP
        # and the remaining part is 'zmq_rep_port'

        # Replace underscores with hyphens if that's a convention, or keep them.
        # For .env, underscores are fine.
        env_var_key = f"PORT_ALLOCATOR_{stripped_key.upper()}"
        output_lines.append(f"{env_var_key}={value}")


    # Sort for consistent output, easier diffing
    output_lines.sort()
    for line in output_lines:
        print(line)

if __name__ == "__main__":
    main()
