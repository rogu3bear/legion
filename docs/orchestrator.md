# Orchestrator Configuration and Port Management

## Dynamic Port Allocation

The Legion Orchestrator supports dynamic port allocation for its services and managed agents.
This is primarily controlled via an `.env.ports` file at the project root.

### `.env.ports` File Contract

- On startup, the orchestrator attempts to read port assignments from an `.env.ports` file.
- This file should contain lines of the format `PORT_ALLOCATOR_<SERVICE_KEY_UPPERCASE>=<port_number>`.
  Example:
  ```env
  PORT_ALLOCATOR_REDIS=5520
  PORT_ALLOCATOR_PROMETHEUS=5540
  ```
- The `scripts/gen_ports_env.sh` script can be used to generate this file based on the `core.utils.ports.PortAllocator` logic, ensuring clustered and conflict-free port assignments.

### Fallback to Defaults

- If `.env.ports` is not found, or if a specific service key is missing from it, the orchestrator will fall back to predefined default ports for known services (e.g., Redis: 6379, Grafana: 3000).

### Accessing Ports

- Agents and internal components can access the configured port for a service using the `legion.ports.get_port("service_key")` utility function.
- The orchestrator also logs a banner on startup (if `LEGION_DEBUG_PORTS=true`) showing the active port assignments:
  ```
  [orchestrator] dynamic ports -> grafana:5540  postgres:5521  prometheus:5541 ...
  ```
