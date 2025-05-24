#!/usr/bin/env python3
"""Send audit status to Discord."""

import json
import time
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from legion.utils.discord_bridge import send_discord_message


async def send_status():
    """Send audit status to Discord."""
    message = json.dumps({
        'ts': int(time.time()),
        'component': 'cursor',
        'branch': 'main',
        'tests': {'backend': 'fail', 'frontend': 'pass'},
        'ports_flagged': 2,
        'dupes_flagged': 1,
        'doc_delta': '/docs/_temp_merge_log.md'
    }, indent=2)
    
    success = await send_discord_message(f'🔧 **Integration Audit Complete**\n```json\n{message}\n```')
    print(f"Status message sent: {success}")


if __name__ == "__main__":
    asyncio.run(send_status()) 