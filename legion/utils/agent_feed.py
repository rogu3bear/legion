import logging
import subprocess
from pathlib import Path


def post_agent_feed(message: str) -> None:
    """Send a message to the agent-feed channel via the Echo agent.

    This helper executes ``scripts/post_agent_feed.sh`` located at the
    repository root. If the script fails, an error is logged.
    """
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "post_agent_feed.sh"
    try:
        subprocess.run([str(script_path), message], check=True)
    except Exception as exc:
        logging.getLogger(__name__).error(
            "Failed to post agent-feed message", exc_info=exc
        )
