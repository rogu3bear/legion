from pathlib import Path


def build_intro(agent_name: str) -> str:
    """Return the intro line for an agent using its prompt file."""
    prompts_dir = Path(__file__).resolve().parents[1] / "prompts"
    prompt_file = prompts_dir / f"{agent_name}.md"
    intro_line = "Ready to assist."
    if prompt_file.exists():
        for line in prompt_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                intro_line = stripped
                break
    return intro_line
