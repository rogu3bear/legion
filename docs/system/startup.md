<!-- File: docs/system/startup.md -->

# System Startup

The orchestrator reads an optional `.env.ports` file during startup. Each line defines a port assignment as `PORT_ALLOCATOR_<SERVICE>=<port>`.

If the file is absent or missing a key, default ports are used. The utility `scripts/gen_ports_env.sh` can generate the file from the built-in allocator.

At boot the orchestrator logs the active assignments when `LEGION_DEBUG_PORTS=true`.
