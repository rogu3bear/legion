#!/usr/bin/env python3
"""CI Test Script for echo_task via Orchestrator"""

import asyncio
import json
import sys
import os

# Add project root to PYTHONPATH to allow imports from legion and core
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from legion.orchestrator import Orchestrator
from core.di_container import container, ILLMClient, IStateManager

def run_echo_test():
    print("CI Test: Running echo_task via orchestrator...")
    try:
        # Initialize orchestrator without PID file for CI
        # Ensure that the DI container is properly initialized if needed by your setup
        # For example, if state_manager or llm_client require specific setup:
        # container.get(IStateManager).setup() # or similar if needed
        # container.get(ILLMClient).configure(...) # or similar if needed

        orchestrator = Orchestrator(
            pid_file=None, # No PID file for testing/CI
            state_manager=container.get(IStateManager),
            llm_client=container.get(ILLMClient)
        )
        
        payload = {"function_tag": "echo_task", "message": "Hello from CI"}
        print(f"CI Test: Dispatching payload: {json.dumps(payload)}")

        # Use dispatch_by_function_tag as it's simpler for this test
        result = orchestrator.dispatch_by_function_tag(payload)
        
        print(f"CI Test Result: {json.dumps(result)}")
        
        # Validate status from the orchestrator's dispatch_by_function_tag method
        assert result.get("status") == "success", \
            f"Orchestrator dispatch status was not 'success'. Got: {result.get("status")}. Full result: {result}"

        # Validate the agent's response nested within the orchestrator's response
        agent_response = result.get("response")
        assert agent_response is not None, f"Agent response was None. Full result: {result}"
        
        assert agent_response.get("status") == "✅ Success", \
            f"Agent response status was not '✅ Success'. Got: {agent_response.get("status")}. Agent response: {agent_response}"
        
        assert "Echoed: Hello from CI" in agent_response.get("result", ""), \
            f"'Echoed: Hello from CI' not found in agent result. Got: {agent_response.get("result")}. Agent response: {agent_response}"
            
        print("CI Test: echo_task successful!")
        
    except AssertionError as ae:
        print(f"CI Test: Assertion Error: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"CI Test: Error running echo_task: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_echo_test() 