#!/usr/bin/env python3
"""
Live test payloads for the orchestrator.
Test Echo, Metrics, and Therapist agents with function_tag based routing.
"""

import json
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from legion.orchestrator import Orchestrator
from core.di_container import container, ILLMClient, IStateManager

def main():
    """Run the four live test payloads through the orchestrator."""

    # Test payloads
    test_payloads = [
        {
            "name": "Echo Test - echo_task",
            "agent": "echo",
            "payload": {
                "function_tag": "echo_task",
                "message": "Hello from test payload 1"
            }
        },
        {
            "name": "Echo Test - log_payload",
            "agent": "echo",
            "payload": {
                "function_tag": "log_payload",
                "payload": {"test": "data", "from": "live_test"}
            }
        },
        {
            "name": "Metrics Test - record_counter",
            "agent": "metrics",
            "payload": {
                "function_tag": "record_counter",
                "counter_name": "test_counter",
                "value": 5
            }
        },
        {
            "name": "Therapist Test - validate_intent",
            "agent": "therapist",
            "payload": {
                "function_tag": "validate_intent",
                "task_details": {
                    "task_id": "test_123",
                    "description": "Test task for validation",
                    "action_type": "validate"
                }
            }
        }
    ]

    # Initialize orchestrator without PID file for testing
    print("Initializing orchestrator...")
    try:
        # Initialize dependencies
        llm_client = container.get(ILLMClient)
        state_manager = container.get(IStateManager)

        orch = Orchestrator(
            pid_file=None,  # No PID file for testing
            state_manager=state_manager,
            llm_client=llm_client
        )

        print("✅ Orchestrator initialized successfully")

        # Run each test payload
        for i, test in enumerate(test_payloads, 1):
            print(f"\n🧪 Test {i}: {test['name']}")
            print(f"   Agent: {test['agent']}")
            print(f"   Payload: {json.dumps(test['payload'], indent=2)}")

            try:
                result = orch.dispatch(test['agent'], test['payload'])
                print(f"   ✅ Result: {json.dumps(result, indent=2)}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

        print("\n🎉 All test payloads completed!")

    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
