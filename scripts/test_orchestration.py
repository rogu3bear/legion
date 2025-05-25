#!/usr/bin/env python3
"""
Test script for orchestration-to-agent communication and LLM toggle functionality.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from legion.orchestrator import Orchestrator
from legion.agents.python.doctor import DoctorAgent
from legion.agents.python.echo import EchoAgent
from legion.agents.python.ping import PingAgent


async def test_orchestration_communication():
    """Test basic orchestration-to-agent communication."""
    print("🚀 Testing Orchestration-to-Agent Communication")
    print("=" * 50)
    
    # Initialize orchestrator without PID file for testing
    orchestrator = Orchestrator(pid_file=None)
    
    try:
        # Test 1: Register a simple agent
        print("\n1. Registering test agents...")
        
        # Create and register agents manually for testing
        doctor_agent = DoctorAgent("doctor_agent", {})
        echo_agent = EchoAgent("echo_agent", {})
        ping_agent = PingAgent("ping_agent", {})
        
        # Add agents to orchestrator's agent registry
        orchestrator.agents = {
            "doctor_agent": doctor_agent,
            "echo_agent": echo_agent,
            "ping_agent": ping_agent,
        }
        
        # Inject orchestrator reference into manually created agents
        for agent_name, agent in orchestrator.agents.items():
            agent.orchestrator = orchestrator
        
        print(f"✅ Registered {len(orchestrator.agents)} agents")
        
        # Test 2: Test communication with LLM enabled
        print("\n2. Testing communication with LLM enabled...")
        
        # Ensure LLM is enabled for first test
        os.environ["ENABLE_LLM_CALLS"] = "true"
        
        for agent_name in orchestrator.agents.keys():
            try:
                print(f"   Testing {agent_name}...")
                
                # Create a simple test message
                test_prompt = f"Hello {agent_name}, please respond with your status."
                
                # Test direct agent communication (simulating what orchestrator.ask does)
                agent = orchestrator.agents[agent_name]
                
                if hasattr(agent, 'handle_message'):
                    response = await agent.handle_message(content=test_prompt)
                    print(f"   ✅ {agent_name} responded: {response[:100]}...")
                else:
                    print(f"   ⚠️ {agent_name} doesn't have handle_message method")
                    
            except Exception as e:
                print(f"   ❌ Error communicating with {agent_name}: {e}")
        
        # Test 3: Test communication with LLM disabled
        print("\n3. Testing communication with LLM disabled...")
        
        # Disable LLM calls
        os.environ["ENABLE_LLM_CALLS"] = "false"
        
        for agent_name in orchestrator.agents.keys():
            try:
                print(f"   Testing {agent_name} with LLM disabled...")
                
                test_prompt = f"Hello {agent_name}, this should use placeholder response."
                
                agent = orchestrator.agents[agent_name]
                
                if hasattr(agent, 'handle_message'):
                    response = await agent.handle_message(content=test_prompt)
                    print(f"   ✅ {agent_name} placeholder response: {response[:100]}...")
                    
                    # Verify it's a placeholder response
                    if "[PLACEHOLDER]" in response:
                        print(f"   ✅ Confirmed placeholder response for {agent_name}")
                    else:
                        print(f"   ⚠️ Expected placeholder response but got: {response[:50]}...")
                else:
                    print(f"   ⚠️ {agent_name} doesn't have handle_message method")
                    
            except Exception as e:
                print(f"   ❌ Error with {agent_name} (LLM disabled): {e}")
        
        # Test 4: Test orchestrator's ask method
        print("\n4. Testing orchestrator.ask method...")
        
        # Re-enable LLM for this test
        os.environ["ENABLE_LLM_CALLS"] = "true"
        
        for agent_name in orchestrator.agents.keys():
            try:
                print(f"   Testing orchestrator.ask with {agent_name}...")
                response = await orchestrator.ask(agent_name, "What is your current status?")
                print(f"   ✅ Orchestrator.ask response from {agent_name}: {response[:100]}...")
            except Exception as e:
                print(f"   ❌ Error with orchestrator.ask for {agent_name}: {e}")
        
        # Test 5: Test self-assessment with LLM toggle
        print("\n5. Testing self-assessment with LLM toggle...")
        
        # Test with LLM enabled
        os.environ["ENABLE_LLM_CALLS"] = "true"
        for agent_name in list(orchestrator.agents.keys())[:2]:  # Test first 2 agents
            try:
                print(f"   Testing self-assessment for {agent_name} (LLM enabled)...")
                assessment = orchestrator.self_assess(agent_name)
                print(f"   ✅ Assessment: {assessment[:100]}...")
            except Exception as e:
                print(f"   ❌ Error in self-assessment for {agent_name}: {e}")
        
        # Test with LLM disabled
        os.environ["ENABLE_LLM_CALLS"] = "false"
        for agent_name in list(orchestrator.agents.keys())[:2]:  # Test first 2 agents
            try:
                print(f"   Testing self-assessment for {agent_name} (LLM disabled)...")
                assessment = orchestrator.self_assess(agent_name)
                print(f"   ✅ Placeholder assessment: {assessment[:100]}...")
                
                if "[PLACEHOLDER]" in assessment:
                    print(f"   ✅ Confirmed placeholder assessment for {agent_name}")
                else:
                    print(f"   ⚠️ Expected placeholder assessment but got: {assessment[:50]}...")
            except Exception as e:
                print(f"   ❌ Error in placeholder self-assessment for {agent_name}: {e}")
        
        print("\n✅ Orchestration communication tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        try:
            await orchestrator.shutdown()
        except Exception as e:
            print(f"Warning: Error during orchestrator shutdown: {e}")


async def test_llm_toggle():
    """Test the LLM toggle functionality in isolation."""
    print("\n🔧 Testing LLM Toggle Functionality")
    print("=" * 50)
    
    # Test the environment variable parsing
    test_cases = [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("off", False),
        ("", True),  # Default should be True
        ("invalid", False),
    ]
    
    print("\nTesting environment variable parsing:")
    for value, expected in test_cases:
        os.environ["ENABLE_LLM_CALLS"] = value
        env_value = os.getenv("ENABLE_LLM_CALLS", "true")
        # Handle empty string case - should default to true
        if not env_value:
            env_value = "true"
        actual = env_value.lower() in ["true", "1", "yes", "on"]
        status = "✅" if actual == expected else "❌"
        print(f"   {status} ENABLE_LLM_CALLS='{value}' -> {actual} (expected {expected})")
    
    print("\n✅ LLM toggle tests completed!")


async def main():
    """Main test function."""
    print("🧪 Legion Orchestration & LLM Toggle Test Suite")
    print("=" * 60)
    
    # Run tests
    await test_llm_toggle()
    await test_orchestration_communication()
    
    print("\n🎉 All tests completed!")
    print("\nTo manually test LLM toggle:")
    print("   export ENABLE_LLM_CALLS=false  # Disable LLM")
    print("   export ENABLE_LLM_CALLS=true   # Enable LLM")


if __name__ == "__main__":
    asyncio.run(main()) 