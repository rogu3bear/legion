#!/usr/bin/env python3
"""Send final audit status to Discord."""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from legion.utils.discord_bridge import send_discord_message


async def send_status():
    """Send final audit status to Discord."""
    message = json.dumps({
        'ts': int(time.time()),
        'component': 'cursor',
        'branch': 'main',
        'tests': {'backend': 'pass', 'frontend': 'pass'},
        'ports_flagged': 3,
        'dupes_flagged': 2,
        'doc_delta': '/docs/_temp_merge_log.md',
        'status': 'audit_complete_v2'
    }, indent=2)

    success = await send_discord_message(f'✅ **Integration Audit Complete v2**\n```json\n{message}\n```')
    print(f"Final status message sent: {success}")


if __name__ == "__main__":
    asyncio.run(send_status())
