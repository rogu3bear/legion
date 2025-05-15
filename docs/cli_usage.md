# Command-Line Interface Usage

The `legion` CLI provides tools to interact with the orchestrator and its agents.

## Commands

### list-agents

Usage:
```bash
legion list-agents
```

Description:
Prints a table of agent keys and their corresponding class names loaded from `legion/configs/agents.yaml`.

### run-agent

Usage:
```bash
legion run-agent <key> [-m/--message "text"]
```

Description:
Loads the specified agent and sends it a message. Default message is `"ping"`.

Arguments:
- `<key>`: Agent key to run.
- `-m/--message`: The message text to send.

Example:
```bash
legion run-agent researcher -m "Analyze data"
```

### show-config

Usage:
```bash
legion show-config
```

Description:
Dumps the raw orchestrator configuration in JSON format.

### ports

Usage:
```bash
legion ports
```

Description:
Displays currently allocated ports for services.

### version

Usage:
```bash
legion version
```

Description:
Prints the Legion package version and Git commit hash, if available.

## Exit Codes

- `0`: Success.
- `2`: Usage error (invalid arguments).
- `3`: Agent load or execution error.
- `1`: Unexpected error or interruption.
