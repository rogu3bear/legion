#!/usr/bin/env python3
"""
Initialize per-agent memory directories and files for all agents defined in agents/.
"""
import os
import glob
import yaml
import json

AGENTS_DIR = "agents"
MEMORY_DIR = "memory"
REQUIRED_FILES = ["memory.json", "task_log.jsonl"]
REQUIRED_SUBDIRS = ["docs"]

def get_agent_names():
    agent_files = glob.glob(os.path.join(AGENTS_DIR, "*.yaml"))
    agent_names = []
    for path in agent_files:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            name = data.get("name")
            if name:
                agent_names.append(name)
    return agent_names

def ensure_agent_memory(agent_name):
    base = os.path.join(MEMORY_DIR, agent_name)
    actions = []
    # Create base dir
    if not os.path.exists(base):
        os.makedirs(base)
        actions.append(f"Created {base}/")
    # Create subdirs
    for sub in REQUIRED_SUBDIRS:
        subdir = os.path.join(base, sub)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
            actions.append(f"Created {subdir}/")
    # Create files
    for fname in REQUIRED_FILES:
        fpath = os.path.join(base, fname)
        if not os.path.exists(fpath):
            with open(fpath, "w", encoding="utf-8") as f:
                if fname.endswith(".json"):
                    json.dump({}, f)
                elif fname.endswith(".jsonl"):
                    pass  # leave empty
            actions.append(f"Created {fpath}")
    return actions

def main():
    agent_names = get_agent_names()
    if not agent_names:
        print("No agent YAMLs found in agents/.")
        return
    for agent in agent_names:
        actions = ensure_agent_memory(agent)
        if actions:
            print(f"[{agent}] Initialized:")
            for act in actions:
                print(f"  - {act}")
        else:
            print(f"[{agent}] Already initialized.")

if __name__ == "__main__":
    main() 