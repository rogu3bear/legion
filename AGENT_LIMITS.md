# AGENT_LIMITS

This document outlines observed limitations of the Codex environment while working on this repository.

## Environment Overview
- Ubuntu-based container with typical Unix utilities
- No network access after setup
- Python and Go toolchains available
- Tests and linting invoked via `make`

## Observed Limitations
1. **No Internet** – Cannot download packages or query remote resources once the environment launches.
2. **External Services Unavailable** – Network-dependent commands such as `apt-get` or `pip install` from the internet fail.
3. **Preinstalled Dependencies** – Must rely on pre-bundled packages and wheels.
4. **File System Scope** – Access restricted to repository files and temporary directories.
5. **Command Execution** – Standard shell commands (e.g., `ls`, `grep`, `python`) work as expected.
6. **Process Limits** – Long-running background processes may be terminated.
7. **No Elevated Privileges** – Cannot modify system-level configuration or install system packages.
8. **No GUI** – All interaction is via command line.

## Workflow Constraints
- Edits must be committed via Git with a clean working tree.
- Tests should be executed with `make test` before committing.
- Must read `agents.md` for repository coordination instructions.
- Should not modify function implementations unless explicitly asked.

## Testing Commands
To gauge capabilities, a loop executed 150 basic shell commands:
```bash
for i in $(seq 1 150); do echo "cmd$i" >/dev/null; done
```
This verified that batch command execution works but provides no network access.

## Additional Tool Tests
The following experiments were performed to explore tool availability:

* **Internet Commands** – Attempting `curl http://example.com` or `sudo apt-get update` hangs until interrupted, confirming network egress is blocked.
* **Local Server** – Running `python3 -m http.server` succeeded and served files over `localhost`, showing local networking is allowed.
* **Log Capture** – Background processes can write logs (e.g., server output captured in `/tmp/server.log`).
* **Process Control** – Jobs can be launched and terminated via standard shell controls but may not run indefinitely.


## Conclusion
Codex operates in a constrained offline environment suited for code editing, running tests, and documentation updates. Network-related tasks or privileged operations are not possible.
