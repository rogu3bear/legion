#!/usr/bin/env python3
"""
Quick test script for Legion MCP Server core functionality.
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path

# Set up test environment
import sys
sys.path.append(str(Path(__file__).parent.parent))

from fastmcp import Client
from mcp_server import mcp


async def test_core_functionality():
    """Test the core MCP server functionality."""
    print("🔧 Testing Legion MCP Server Core Functionality")
    print("=" * 60)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            async with Client(mcp) as client:
                agent_name = "test_agent"
                
                # Test 1: Set agent memory
                print("1. Testing agent memory operations...")
                result = await client.call_tool("set_agent_memory", {
                    "agent_name": agent_name,
                    "key": "status",
                    "value": "testing"
                })
                data = json.loads(result[0].text)
                assert data["status"] == "success"
                print("   ✅ Memory set successfully")
                
                # Test 2: Get agent memory
                result = await client.call_tool("get_agent_memory", {
                    "agent_name": agent_name,
                    "key": "status"
                })
                data = json.loads(result[0].text)
                assert data["value"] == "testing"
                print("   ✅ Memory retrieved successfully")
                
                # Test 3: Log a task
                print("2. Testing task logging...")
                result = await client.call_tool("log_agent_task", {
                    "agent_name": agent_name,
                    "task_data": {
                        "action": "test_action",
                        "status": "completed"
                    }
                })
                data = json.loads(result[0].text)
                assert data["status"] == "success"
                print("   ✅ Task logged successfully")
                
                # Test 4: Get system status
                print("3. Testing system status...")
                result = await client.call_tool("get_legion_system_status", {})
                data = json.loads(result[0].text)
                assert data["mcp_server"] == "active"
                assert "llm" in data
                print("   ✅ System status retrieved successfully")
                print(f"   📊 LLM Provider: {data['llm'].get('provider', 'unknown')}")
                print(f"   📊 LLM Available: {data['llm'].get('available', False)}")
                
                # Test 5: Text summarization (if LLM available)
                print("4. Testing text summarization...")
                test_text = "This is a test text for summarization. " * 10
                result = await client.call_tool("summarize_content", {
                    "text": test_text,
                    "max_length": 100
                })
                data = json.loads(result[0].text)
                assert "summary" in data
                print("   ✅ Text summarization successful")
                print(f"   📝 Original length: {data['original_length']}")
                print(f"   📝 Summary length: {data['summary_length']}")
                
                # Test 6: LLM status
                print("5. Testing LLM status...")
                result = await client.call_tool("get_llm_status", {})
                data = json.loads(result[0].text)
                assert data["llm_available"] is not None
                print("   ✅ LLM status retrieved successfully")
                
                # Test 7: Document operations
                print("6. Testing document operations...")
                result = await client.call_tool("save_agent_document", {
                    "agent_name": agent_name,
                    "document_name": "test.txt",
                    "content": "Test document content"
                })
                data = json.loads(result[0].text)
                assert data["status"] == "success"
                print("   ✅ Document saved successfully")
                
                result = await client.call_tool("list_agent_documents", {
                    "agent_name": agent_name
                })
                data = json.loads(result[0].text)
                assert data["document_count"] > 0
                print("   ✅ Document list retrieved successfully")
                
                # Test 8: Web search
                print("7. Testing web search...")
                result = await client.call_tool("perform_web_search", {
                    "query": "test query",
                    "sources": ["web"]
                })
                data = json.loads(result[0].text)
                assert "results" in data
                print("   ✅ Web search successful")
                
                # Test 9: Vector memory (basic)
                print("8. Testing vector memory...")
                result = await client.call_tool("store_vector_memories", {
                    "agent_name": agent_name,
                    "memory_snippets": [
                        {
                            "text": "Test memory",
                            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
                        }
                    ]
                })
                data = json.loads(result[0].text)
                assert data["status"] == "success"
                print("   ✅ Vector memory stored successfully")
                
                print("\n" + "=" * 60)
                print("🎉 All core functionality tests PASSED!")
                print("=" * 60)
                
                return True
                
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            os.chdir(original_cwd)


async def test_llm_integration():
    """Test LLM integration if available."""
    print("\n🤖 Testing LLM Integration")
    print("=" * 40)
    
    async with Client(mcp) as client:
        try:
            # Test direct LLM interaction
            result = await client.call_tool("ask_llm", {
                "prompt": "What is 2 + 2?",
                "max_tokens": 50
            })
            data = json.loads(result[0].text)
            
            if data.get("success"):
                print("   ✅ Direct LLM interaction successful")
                print(f"   🧠 Provider: {data.get('provider', 'unknown')}")
                print(f"   💬 Response: {data.get('response', 'No response')[:100]}...")
            else:
                print("   ⚠️  LLM interaction failed (may be expected if no LLM configured)")
                print(f"   🔍 Error: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ⚠️  LLM test error: {e}")


if __name__ == "__main__":
    async def main():
        success = await test_core_functionality()
        await test_llm_integration()
        
        if success:
            print("\n🚀 Legion MCP Server is fully functional!")
            print("\nNext steps:")
            print("1. Configure your LLM provider (LM Studio/OpenAI)")
            print("2. Run: python skills/mcp_server.py")
            print("3. Connect your MCP client applications")
        else:
            print("\n💥 Some tests failed. Check the errors above.")
            exit(1)
    
    asyncio.run(main()) 