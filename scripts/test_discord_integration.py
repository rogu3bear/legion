#!/usr/bin/env python3
"""Test script for Discord integration with Legion agents."""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from legion.utils.discord_bridge import (
    send_discord_message,
    send_discord_action,
    send_discord_embed,
    MessageType,
    create_orchestrator_callback
)


async def test_basic_messaging():
    """Test basic Discord messaging functionality."""
    print("Testing basic Discord messaging...")

    # Test simple message
    success = await send_discord_message("🔧 Testing basic message from integration script")
    print(f"Simple message sent: {success}")

    # Test action message
    success = await send_discord_action({
        "type": "test_action",
        "source": "test_discord_integration.py",
        "status": "operational",
        "timestamp": "2025-01-24T06:00:00Z"
    })
    print(f"Action message sent: {success}")

    # Test different message types
    for msg_type, description in [
        (MessageType.INFO, "This is an informational message"),
        (MessageType.SUCCESS, "This is a success message"),
        (MessageType.WARNING, "This is a warning message"),
        (MessageType.ERROR, "This is an error message (test only)")
    ]:
        success = await send_discord_embed(
            "TestBot",
            description,
            msg_type,
            fields=[
                ("Message Type", msg_type.value),
                ("Test Status", "Active"),
                ("Timestamp", "2025-01-24")
            ]
        )
        print(f"{msg_type.value.title()} message sent: {success}")
        await asyncio.sleep(1)  # Avoid rate limiting


async def test_agent_simulation():
    """Simulate agent behavior using the new Discord integration."""
    print("\nTesting agent simulation...")

    # Simulate metrics agent report
    await send_discord_embed(
        "MetricsAgent",
        "System metrics report generated",
        MessageType.SUCCESS,
        fields=[
            ("CPU Usage", "45%"),
            ("Memory Usage", "2.1 GB"),
            ("Active Agents", "5"),
            ("Messages Processed", "127"),
            ("Uptime", "4h 23m")
        ]
    )

    # Simulate architect agent status
    await send_discord_embed(
        "ArchitectAgent",
        "Codebase review completed",
        MessageType.INFO,
        fields=[
            ("Files Analyzed", "42"),
            ("Issues Found", "3"),
            ("Suggestions", "7"),
            ("Code Quality", "Good")
        ]
    )

    # Simulate healthcheck agent
    await send_discord_embed(
        "HealthcheckAgent",
        "All systems operational",
        MessageType.SUCCESS,
        fields=[
            ("Database", "✅ Connected"),
            ("API Endpoints", "✅ Responding"),
            ("Discord Bot", "✅ Online"),
            ("Memory Usage", "✅ Normal")
        ]
    )

    # Simulate error scenario
    await send_discord_embed(
        "TherapistAgent",
        "Validation check failed",
        MessageType.ERROR,
        fields=[
            ("Error Code", "VAL_001"),
            ("Affected Component", "Message Processor"),
            ("Retry Attempt", "3/3"),
            ("Action Required", "Manual Review")
        ]
    )


async def test_orchestrator_integration():
    """Test integration with orchestrator callback."""
    print("\nTesting orchestrator integration...")

    # Create orchestrator callback
    callback = create_orchestrator_callback()

    # Simulate orchestrator messages
    test_messages = [
        ("doctor_agent", "Completed health assessment of agent cluster"),
        ("researcher_agent", "Finished data collection and analysis"),
        ("ping_agent", "Network connectivity verified across all nodes"),
        ("echo_agent", "Message relay system functioning normally")
    ]

    for agent_name, message in test_messages:
        await callback(agent_name, message)
        await asyncio.sleep(1)


async def main():
    """Run all Discord integration tests."""
    print("🚀 Starting Discord Integration Tests")
    print("=" * 50)

    try:
        await test_basic_messaging()
        await asyncio.sleep(2)

        await test_agent_simulation()
        await asyncio.sleep(2)

        await test_orchestrator_integration()

        print("\n✅ All Discord integration tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
