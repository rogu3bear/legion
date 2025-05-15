#!/usr/bin/env python3
"""
Scans Python agent modules in legion/agents/python/
and intelligently merges them with legion/configs/agents.yaml,
preserving existing configurations and comments where possible.

Requires: ruamel.yaml (pip install ruamel.yaml)
"""

import re
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

AGENT_DIR = Path(__file__).parent.parent / "legion" / "agents" / "python"
CONFIG_FILE = Path(__file__).parent.parent / "legion" / "configs" / "agents.yaml"
DEFAULT_CHANNEL_ID = 0  # Placeholder
DEFAULT_LLM_MODEL = "meta-llama-3.1-8b-instruct"  # Placeholder


def map_agent_keys_to_class_names():
    """
    Scans agent modules and returns a dictionary mapping agent keys
    (derived from module names, with disambiguation for multiple classes per file)
    to their respective class names.
    Example: {'architect': 'ArchitectAgent', 'helper': 'HelperAgent', 'helper1': 'AnotherHelperAgent'}
    """
    agent_key_to_class = {}
    # Sort file processing for deterministic key generation if multiple classes are in one file
    for filepath in sorted(AGENT_DIR.glob("*.py")):
        if filepath.name == "__init__.py":
            continue

        module_name = filepath.stem
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Find class definitions like "class ArchitectAgent(...):"
            class_matches = re.findall(
                r"^class\s+([a-zA-Z_][a-zA-Z0-9_]*Agent)\s*\(", content, re.MULTILINE
            )

            if class_matches:
                # temp_keys_for_module = [] # Not strictly needed if global agent_key_to_class is checked
                for class_name in class_matches:
                    agent_key_base = module_name
                    current_agent_key = agent_key_base
                    counter = 1
                    # Ensure unique key across all discovered agents so far
                    while current_agent_key in agent_key_to_class:
                        current_agent_key = f"{agent_key_base}{counter}"
                        counter += 1

                    agent_key_to_class[current_agent_key] = class_name
                    # temp_keys_for_module.append(current_agent_key)
                    print(
                        f"Discovered: key='{current_agent_key}', class='{class_name}' (from module='{module_name}.py')"
                    )
            # else:
            # print(f"No agent classes found in {filepath.name}") # Less verbose

        except Exception as e:
            print(f"Error processing file {filepath.name} for class mapping: {e}")

    return agent_key_to_class


def get_default_agent_config(agent_key: str, class_name: str) -> CommentedMap:
    """Returns a default configuration structure for a new agent."""
    return CommentedMap(
        {
            "name": agent_key,
            "class": class_name,
            "prompt": f"You are the {agent_key} agent. Your responsibility is to ...",
            "user_prompt": "{event_content}",
            "channel_id": DEFAULT_CHANNEL_ID,
            "llm_model": DEFAULT_LLM_MODEL,
            "temperature": 0.7,
            "max_tokens": 1024,
            "memory_top_k": 5,
        }
    )


def write_config_ruamel(config_data: CommentedMap, yaml_instance: YAML):
    """Writes the generated agent configurations to agents.yaml using ruamel.yaml."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml_instance.dump(config_data, f)
        print(f"Successfully wrote agent configurations to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error writing config file {CONFIG_FILE}: {e}")


def main():
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)  # Standard YAML formatting
    # yaml.width = 1000 # To prevent line wrapping if desired, similar to old script

    existing_config = CommentedMap()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                loaded_data = yaml.load(f)
            if isinstance(
                loaded_data, dict
            ):  # Check if load returned a dict-like structure
                existing_config = loaded_data
            else:
                print(
                    f"Warning: Existing config file {CONFIG_FILE} is empty or not valid YAML. Starting fresh."
                )
        except Exception as e:
            print(
                f"Error loading existing config from {CONFIG_FILE}: {e}. Starting fresh."
            )

    print(f"Scanning for agent classes in: {AGENT_DIR}")
    discovered_key_to_class_map = map_agent_keys_to_class_names()

    final_config = CommentedMap()
    processed_keys = set()

    # Merge: Update existing agents or add new ones based on discovery
    for agent_key, discovered_class_name in discovered_key_to_class_map.items():
        processed_keys.add(agent_key)
        if agent_key in existing_config:
            print(f"Updating existing agent: '{agent_key}'")
            final_config[agent_key] = existing_config[
                agent_key
            ]  # Preserve existing entry structure and comments
            final_config[agent_key]["class"] = (
                discovered_class_name  # Update class name
            )

            # Ensure 'name' field matches the agent_key for consistency
            if final_config[agent_key].get("name") != agent_key:
                print(
                    f"  Aligning 'name' field for agent key '{agent_key}' to '{agent_key}'. Was: '{final_config[agent_key].get('name')}'"
                )
                final_config[agent_key]["name"] = agent_key
        else:
            print(
                f"Adding new agent: '{agent_key}' with class '{discovered_class_name}'"
            )
            final_config[agent_key] = get_default_agent_config(
                agent_key, discovered_class_name
            )

    # Identify and warn about obsolete keys (present in old config but not discovered)
    obsolete_keys = set(existing_config.keys()) - processed_keys
    if obsolete_keys:
        print("\n--- Obsolete Agent Keys ---")
        for key in obsolete_keys:
            print(
                f"Warning: Agent key '{key}' (class: {existing_config[key].get('class', 'N/A')}) was in {CONFIG_FILE} but no corresponding agent module/class was discovered. This entry will be REMOVED."
            )
        print("---------------------------")

    # Add any remaining keys from existing_config that were not processed (e.g. top-level comments or non-agent keys)
    # This is tricky with ruamel.yaml if we want to preserve order and comments perfectly around deleted blocks.
    # For now, the final_config is built only from processed_keys (active or newly added agents).
    # If preserving other top-level structures is crucial, a more sophisticated merge or a different approach
    # to constructing final_config (e.g., by deleting obsolete keys from a copy of existing_config) would be needed.

    if not final_config and not discovered_key_to_class_map:
        print("No agents discovered and no existing configuration to write.")
    else:
        write_config_ruamel(final_config, yaml_instance=yaml)


if __name__ == "__main__":
    main()
