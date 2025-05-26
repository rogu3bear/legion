import os
import json
from pathlib import Path
import html
import redis
from redis import Redis

R = None
REDIS_HOST = os.getenv("LEGION_REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("LEGION_REDIS_PORT", 7600))

def get_redis_client():
    global R
    if R is None:
        try:
            R = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=1)
            R.ping()
        except redis.exceptions.ConnectionError as e:
            print(f"Initial Redis connection failed: {e}")
            R = None
            raise
    elif not R.ping():
        try:
            R = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=1)
            R.ping()
        except redis.exceptions.ConnectionError as e:
            print(f"Re-establishing Redis connection failed: {e}")
            R = None
            raise
    return R

REG_PATH = Path("legion/registry/agent_registry.json")
PROMPT_HISTORY_MAX_LEN = 5
PROMPT_EVENTS_CHANNEL = "prompts:events"

def _handle_redis_error(func):
    def wrapper(*args, **kwargs):
        try:
            client = get_redis_client()
            if client is None:
                raise redis.exceptions.ConnectionError("Redis client is not available.")
            return func(client, *args, **kwargs)
        except redis.exceptions.ConnectionError as e:
            raise redis.exceptions.ConnectionError(f"Redis connection error: {e}") from e
        except Exception as e:
            raise Exception(f"An unexpected error occurred in prompt_repo: {e}") from e
    return wrapper

@_handle_redis_error
def all_agents(client: Redis):
    """Return the full agent registry with system prompts from agent files."""
    registry_data = json.loads(REG_PATH.read_text())

    processed_registry = {}
    for agent_name, agent_config in registry_data.items():
        current_system_prompt, current_skills = get_prompt(client, agent_name)
        processed_registry[agent_name] = {
            **agent_config,
            "system_prompt": current_system_prompt,
            "function_tags": current_skills,
            "default_system_prompt": _get_default_system_prompt(agent_name),
            "default_function_tags": agent_config.get("function_tags", [])
        }
    return processed_registry

def _get_default_system_prompt(agent_name: str) -> str:
    """Get the default system prompt from the agent's Python file."""
    agent_file = Path(f"legion/agents/python/{agent_name}.py")

    if not agent_file.exists():
        return "You are a helpful assistant."

    try:
        content = agent_file.read_text()

        prompt_match_single_line = None
        prompt_match_multi_line_block = None

        patterns_to_check = [
            f'{agent_name}.system_prompt = ',
            'system_prompt = ',
            'SYSTEM_PROMPT = '
        ]

        found_prompt_value = None

        for line_idx, line in enumerate(content.splitlines()):
            stripped_line = line.strip()
            for pattern in patterns_to_check:
                if stripped_line.startswith(pattern):
                    value_part = stripped_line[len(pattern):].strip()

                    if value_part.startswith('(') and value_part.endswith(')'):
                        value_part = value_part[1:-1].strip()

                    if value_part.startswith('"""') or value_part.startswith("'''"):
                        quote_type = value_part[:3]
                        if value_part.endswith(quote_type) and value_part.count(quote_type) >=2 :
                             found_prompt_value = value_part[3:-3]
                             break
                        else:
                            prompt_lines = [value_part[3:]]
                            for next_line_idx in range(line_idx + 1, len(content.splitlines())):
                                current_block_line = content.splitlines()[next_line_idx].strip()
                                if current_block_line.endswith(quote_type):
                                    prompt_lines.append(current_block_line[:-3])
                                    found_prompt_value = "\n".join(prompt_lines)
                                    break
                                else:
                                    prompt_lines.append(current_block_line)
                            if found_prompt_value: break
                    elif value_part.startswith('"') and value_part.endswith('"'):
                        found_prompt_value = value_part[1:-1]
                        break
                    elif value_part.startswith("'") and value_part.endswith("'"):
                         found_prompt_value = value_part[1:-1]
                         break
            if found_prompt_value:
                return found_prompt_value.replace('\\n', '\n').replace('\\t', '\t')

        return "You are a helpful assistant."
    except Exception as e:
        return "You are a helpful assistant."

@_handle_redis_error
def get_prompt(client: Redis, agent: str):
    """Get system prompt and skills for an agent, Redis override first, then registry fallback."""
    redis_key = f"prompts:{agent}"
    data = client.get(redis_key)
    if data:
        override = json.loads(data)
        return html.unescape(override["system"]), override["skills"]

    default_prompt = _get_default_system_prompt(agent)

    registry_data = json.loads(REG_PATH.read_text())
    default_skills = registry_data.get(agent, {}).get("function_tags", [])

    return default_prompt, default_skills

@_handle_redis_error
def save_prompt(client: Redis, agent: str, system: str, skills: list[str]):
    """Save system prompt and skills override to Redis, manage history, and publish event."""
    redis_key = f"prompts:{agent}"
    history_key = f"{redis_key}:history"

    current_data_json = client.get(redis_key)
    if current_data_json:
        current_prompt_data = json.loads(current_data_json)
        client.lpush(history_key, json.dumps(current_prompt_data))
        client.ltrim(history_key, 0, PROMPT_HISTORY_MAX_LEN - 1)

    escaped_system_prompt = html.escape(system)

    new_prompt_data = {"system": escaped_system_prompt, "skills": skills}
    client.set(redis_key, json.dumps(new_prompt_data))

    event_payload = {
        "agent": agent,
        "event": "prompt_updated",
        "payload": {"system": escaped_system_prompt, "skills": skills}
    }
    client.publish(PROMPT_EVENTS_CHANNEL, json.dumps(event_payload))
    return new_prompt_data

@_handle_redis_error
def get_all_skills(client: Redis):
    """Get union of all skills from agent_registry.json AND Redis overrides."""
    registry_data = json.loads(REG_PATH.read_text())
    all_skills = set()

    for agent_data in registry_data.values():
        all_skills.update(agent_data.get("function_tags", []))

    prompt_keys = client.keys("prompts:*:history")
    agent_override_keys = [k for k in client.keys("prompts:*") if not k.endswith(":history")]

    for key in agent_override_keys:
        data_json = client.get(key)
        if data_json:
            try:
                data = json.loads(data_json)
                if "skills" in data and isinstance(data["skills"], list):
                    all_skills.update(data["skills"])
            except json.JSONDecodeError:
                print(f"Warning: Malformed JSON in Redis key {key}")
                pass

    return sorted(list(all_skills))

@_handle_redis_error
def revert_prompt(client: Redis, agent: str):
    """Reverts to the last prompt in history, saves it as current, and publishes event."""
    redis_key = f"prompts:{agent}"
    history_key = f"{redis_key}:history"

    last_version_json = client.lpop(history_key)
    if not last_version_json:
        return None

    last_version_data = json.loads(last_version_json)

    client.set(redis_key, json.dumps(last_version_data))

    event_payload = {
        "agent": agent,
        "event": "prompt_updated",
        "payload": last_version_data
    }
    client.publish(PROMPT_EVENTS_CHANNEL, json.dumps(event_payload))

    return {"system": html.unescape(last_version_data["system"]), "skills": last_version_data["skills"]}

# Initial call to set up R (optional, can be deferred to first use)
# try:
#     get_redis_client()
# except redis.exceptions.ConnectionError:
#     print("Failed to connect to Redis on module load. Will try again on first use.")
#     pass
