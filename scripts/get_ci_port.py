#!/usr/bin/env python3
"""Helper script for CI to fetch specific port values from UnifiedPortManager."""

import os
import sys

# Ensure the script can find the legion module.
# This might be needed if running from the scripts directory directly in CI.
# Adjust the path as necessary based on your project structure and CI execution context.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

try:
    from legion.ports import unified_port_manager
except ImportError as e:
    print(
        f"Error importing UnifiedPortManager: {e}. Check PYTHONPATH or script location.",
        file=sys.stderr,
    )
    sys.exit(2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python scripts/get_ci_port.py <service_group> <component_key>",
            file=sys.stderr,
        )
        sys.exit(1)

    service_group = sys.argv[1]
    component_key = sys.argv[2]

    # unified_port_manager loads ports.yaml on its first instantiation (when imported)
    port = unified_port_manager.get_port(service_group, component_key)

    if port is not None:
        print(port)
        sys.exit(0)
    else:
        print(
            f"Port not found for {service_group}.{component_key} in ports.yaml",
            file=sys.stderr,
        )
        # Try to load and print all available ports for debugging if LEGION_DEBUG_PORTS is set
        if os.getenv("LEGION_DEBUG_PORTS", "false").lower() == "true":
            print("Available ports for debugging:", file=sys.stderr)
            all_ports = unified_port_manager.get_all_resolved_ports()
            if all_ports:
                for key, val in all_ports.items():
                    print(f"  {key}: {val}", file=sys.stderr)
            else:
                print("  No ports resolved at all.", file=sys.stderr)
        sys.exit(1)  # Exit with error if specific port not found
