#!/usr/bin/env python3
"""
Command-line interface for Legion.
"""

import argparse
import asyncio
import json
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version

from legion.orchestrator import AgentLoadError, Orchestrator


def main():
    parser = argparse.ArgumentParser(prog="legion")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # list-agents command
    subparsers.add_parser(
        "list-agents",
        help="Print a table of agent keys and class names from agents.yaml.",
    )

    # run-agent command
    run_parser = subparsers.add_parser(
        "run-agent", help="Load the agent and send a message."
    )
    run_parser.add_argument("key", help="Agent key to run")
    run_parser.add_argument(
        "-m", "--message", default="ping", help="Message to send to the agent"
    )

    # show-config command
    subparsers.add_parser(
        "show-config", help="Dump the raw orchestrator config (YAML → JSON)."
    )

    # ports command
    subparsers.add_parser("ports", help="Show allocated ports (service → port).")

    # version command
    subparsers.add_parser("version", help="Print Legion version and Git commit hash.")

    args = parser.parse_args()

    try:
        if args.command == "list-agents":
            orch = Orchestrator(pid_file=None, state_manager=None, llm_client=None)
            for key, cfg in orch.config.items():
                class_name = cfg.get("class", "<unknown>")
                print(f"{key}\t{class_name}")
            sys.exit(0)

        if args.command == "run-agent":
            orch = Orchestrator(pid_file=None, state_manager=None, llm_client=None)
            key = args.key
            try:
                orch.load_agent(key)
                payload = {"message": args.message}
                dispatch_fn = orch.dispatch
                if asyncio.iscoroutinefunction(dispatch_fn):
                    result = asyncio.run(dispatch_fn(key, payload))
                else:
                    result = dispatch_fn(key, payload)
                print(json.dumps(result, indent=2))
                sys.exit(0)
            except AgentLoadError as e:
                print(f"Error loading agent {key}: {e}", file=sys.stderr)
                sys.exit(3)
            except Exception as e:
                print(f"Agent error: {e}", file=sys.stderr)
                sys.exit(3)

        if args.command == "show-config":
            orch = Orchestrator(pid_file=None, state_manager=None, llm_client=None)
            print(json.dumps(orch.config, indent=2))
            sys.exit(0)

        if args.command == "ports":
            orch = Orchestrator(pid_file=None, state_manager=None, llm_client=None)
            # Get all resolved ports from UnifiedPortManager
            resolved_ports = orch.port_allocator.get_all_resolved_ports()
            if resolved_ports:
                # Sort by the full key for consistent output
                for full_key, port in sorted(resolved_ports.items()):
                    print(f"{full_key}\t{port}")
            else:
                print("No ports configured or resolved.")
            sys.exit(0)

        if args.command == "version":
            ver = "unknown"
            try:
                ver = version("legion")
            except PackageNotFoundError:
                pass
            git_rev = ""
            try:
                git_rev = (
                    subprocess.check_output(
                        ["git", "rev-parse", "--short", "HEAD"],
                        stderr=subprocess.DEVNULL,
                    )
                    .decode()
                    .strip()
                )
            except Exception:
                pass
            if git_rev:
                print(f"{ver}+{git_rev}")
            else:
                print(ver)
            sys.exit(0)

    except KeyboardInterrupt:
        sys.exit(1)
