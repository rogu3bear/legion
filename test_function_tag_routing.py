#!/usr/bin/env python3
"""
Test function-tag based routing.
This tests Step 2: function-tag → agent lookup table.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from legion.orchestrator import Orchestrator
from core.di_container import container, ILLMClient, IStateManager

def main():
    """Test function-tag based routing."""
    
    print("🧪 Testing Function-Tag Based Routing")
    print("=" * 50)
    
    try:
        # Initialize orchestrator
        print("Initializing orchestrator...")
        orchestrator = Orchestrator(
            state_manager=container.get(IStateManager),
            llm_client=container.get(ILLMClient),
        )
        print("✅ Orchestrator initialized successfully")
        
        # Test payloads with only function_tag (no agent specified)
        test_payloads = [
            {
                "name": "Function-tag routing: echo_task",
                "payload": {
                    "function_tag": "echo_task",
                    "message": "Hello via function-tag routing!"
                }
            },
            {
                "name": "Function-tag routing: record_counter", 
                "payload": {
                    "function_tag": "record_counter",
                    "counter_name": "function_tag_test",
                    "value": 10
                }
            },
            {
                "name": "Function-tag routing: validate_intent",
                "payload": {
                    "function_tag": "validate_intent",
                    "task_details": {
                        "task_id": "ft_test_456",
                        "description": "Function-tag routing test",
                        "action_type": "validate"
                    }
                }
            },
            {
                "name": "Function-tag routing: unknown_function",
                "payload": {
                    "function_tag": "unknown_function",
                    "data": "should fail"
                }
            }
        ]
        
        # Run tests
        for i, test in enumerate(test_payloads, 1):
            print(f"\n🧪 Test {i}: {test['name']}")
            print(f"   Payload: {json.dumps(test['payload'], indent=2)}")
            
            try:
                result = orchestrator.dispatch_by_function_tag(test['payload'])
                print(f"   ✅ Result: {json.dumps(result, indent=2)}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n🎉 Function-tag routing tests completed!")
        
    except Exception as e:
        print(f"❌ Failed to test function-tag routing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 