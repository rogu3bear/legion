#!/usr/bin/env python3
"""
Script to scan the repository for direct instantiations of agent classes
outside of test directories, suggesting use of orchestrator.load_agent.
"""

import ast
import os
import sys

AGENT_CLASSES = {
    "ArchitectAgent",
    "TherapistAgent",
    "MetricsAgent",
    "UxDesignerAgent",
    "PingAgent",
    "EchoAgent",
    "HealthcheckAgent",
}

IGNORED_DIRS = {"tests", "test", "__pycache__"}


def is_in_test_dir(path):
    parts = set(path.split(os.sep))
    return bool(parts & IGNORED_DIRS)


def check_file(path):
    # Skip files in test directories
    if is_in_test_dir(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except (SyntaxError, UnicodeDecodeError):
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in AGENT_CLASSES:
                print(
                    f"{path}:{node.lineno}: Direct instantiation of {name} found; "
                    f"use orchestrator.load_agent('{name.lower()}') instead."
                )


def main(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            full_path = os.path.join(dirpath, filename)
            check_file(full_path)


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    main(root)
