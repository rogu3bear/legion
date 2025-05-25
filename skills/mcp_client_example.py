"""
Legion MCP Client Example

This script demonstrates how to use the Legion MCP server to interact with
Legion agents, memory systems, and skills. It shows both in-memory testing
and remote server usage patterns.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from fastmcp import Client
from mcp_server import mcp


async def demonstrate_agent_memory_operations():
    """Demonstrate agent memory operations through MCP."""
    print("\n=== Agent Memory Operations ===")
    
    async with Client(mcp) as client:
        agent_name = "demo_agent"
        
        # Set some memory values
        print(f"Setting memory for {agent_name}...")
        result = await client.call_tool("set_agent_memory", {
            "agent_name": agent_name,
            "key": "current_task",
            "value": "processing_data"
        })
        print(f"Result: {json.loads(result[0].text)}")
        
        # Set configuration
        result = await client.call_tool("set_agent_memory", {
            "agent_name": agent_name,
            "key": "config",
            "value": {
                "max_retries": 5,
                "timeout_seconds": 30,
                "debug_mode": True
            }
        })
        print(f"Config set: {json.loads(result[0].text)}")
        
        # Retrieve all memory
        print(f"\nRetrieving all memory for {agent_name}...")
        result = await client.call_tool("get_agent_memory", {
            "agent_name": agent_name
        })
        memory_data = json.loads(result[0].text)
        print(f"Memory data: {json.dumps(memory_data, indent=2)}")
        
        # Retrieve specific key
        print(f"\nRetrieving specific key 'current_task'...")
        result = await client.call_tool("get_agent_memory", {
            "agent_name": agent_name,
            "key": "current_task"
        })
        specific_data = json.loads(result[0].text)
        print(f"Specific key data: {json.dumps(specific_data, indent=2)}")


async def demonstrate_task_logging():
    """Demonstrate task logging functionality."""
    print("\n=== Task Logging ===")
    
    async with Client(mcp) as client:
        agent_name = "demo_agent"
        
        # Log various tasks
        tasks = [
            {
                "action": "initialize",
                "status": "completed",
                "duration_ms": 150,
                "metadata": {"version": "1.0"}
            },
            {
                "action": "process_data",
                "status": "running",
                "progress": 0.75,
                "eta_seconds": 30
            },
            {
                "action": "cleanup",
                "status": "pending",
                "priority": "low"
            }
        ]
        
        print(f"Logging {len(tasks)} tasks for {agent_name}...")
        for task in tasks:
            result = await client.call_tool("log_agent_task", {
                "agent_name": agent_name,
                "task_data": task
            })
            log_result = json.loads(result[0].text)
            print(f"Logged: {task['action']} - {log_result['status']}")
        
        # Retrieve task log
        print(f"\nRetrieving task log for {agent_name}...")
        result = await client.call_tool("get_agent_task_log", {
            "agent_name": agent_name
        })
        log_data = json.loads(result[0].text)
        print(f"Task count: {log_data['task_count']}")
        print("Recent tasks:")
        for i, task in enumerate(log_data['tasks'][:3]):  # Show first 3
            print(f"  {i+1}. {task.get('action', 'unknown')} - {task.get('status', 'unknown')}")


async def demonstrate_document_management():
    """Demonstrate document management functionality."""
    print("\n=== Document Management ===")
    
    async with Client(mcp) as client:
        agent_name = "demo_agent"
        
        # Save documents
        documents = [
            {
                "name": "agent_config.yaml",
                "content": """
name: demo_agent
version: 1.0
settings:
  max_memory_mb: 512
  log_level: INFO
  auto_save: true
"""
            },
            {
                "name": "task_plan.md",
                "content": """
# Task Execution Plan

## Current Tasks
1. Initialize agent memory
2. Process incoming data
3. Log all activities
4. Clean up resources

## Status
- Phase 1: Complete
- Phase 2: In Progress (75%)
- Phase 3: Pending
"""
            }
        ]
        
        print(f"Saving {len(documents)} documents for {agent_name}...")
        for doc in documents:
            result = await client.call_tool("save_agent_document", {
                "agent_name": agent_name,
                "document_name": doc["name"],
                "content": doc["content"]
            })
            save_result = json.loads(result[0].text)
            print(f"Saved: {doc['name']} - {save_result['status']}")
        
        # List documents
        print(f"\nListing documents for {agent_name}...")
        result = await client.call_tool("list_agent_documents", {
            "agent_name": agent_name
        })
        doc_list = json.loads(result[0].text)
        print(f"Document count: {doc_list['document_count']}")
        for doc in doc_list['documents']:
            print(f"  - {doc}")
        
        # Retrieve a specific document
        print(f"\nRetrieving 'task_plan.md'...")
        result = await client.call_tool("get_agent_document", {
            "agent_name": agent_name,
            "document_name": "task_plan.md"
        })
        doc_data = json.loads(result[0].text)
        if doc_data['status'] == 'success':
            print(f"Document content preview:")
            lines = doc_data['content'].split('\n')[:5]
            for line in lines:
                print(f"  {line}")
            print("  ...")


async def demonstrate_vector_memory_search():
    """Demonstrate vector memory storage and search."""
    print("\n=== Vector Memory Search ===")
    
    async with Client(mcp) as client:
        agent_name = "demo_agent"
        
        # Store vector memories (simulated embeddings)
        memory_snippets = [
            {
                "text": "Agent successfully initialized with default configuration",
                "embedding": [0.1, 0.8, 0.3, 0.6, 0.2]
            },
            {
                "text": "Data processing completed with 95% accuracy",
                "embedding": [0.7, 0.2, 0.9, 0.1, 0.5]
            },
            {
                "text": "Error encountered during network communication",
                "embedding": [0.3, 0.1, 0.2, 0.9, 0.8]
            },
            {
                "text": "Memory usage optimization resulted in 20% improvement",
                "embedding": [0.5, 0.6, 0.4, 0.3, 0.7]
            }
        ]
        
        print(f"Storing {len(memory_snippets)} vector memories for {agent_name}...")
        result = await client.call_tool("store_vector_memories", {
            "agent_name": agent_name,
            "memory_snippets": memory_snippets
        })
        store_result = json.loads(result[0].text)
        print(f"Stored: {store_result['stored_count']} memories")
        
        # Search for similar memories
        search_queries = [
            {
                "name": "initialization_query",
                "embedding": [0.2, 0.7, 0.4, 0.5, 0.3],  # Similar to initialization
                "description": "Looking for initialization-related memories"
            },
            {
                "name": "error_query", 
                "embedding": [0.4, 0.2, 0.1, 0.8, 0.9],  # Similar to error
                "description": "Looking for error-related memories"
            }
        ]
        
        for query in search_queries:
            print(f"\nSearching with {query['name']} ({query['description']})...")
            result = await client.call_tool("search_vector_memories", {
                "agent_name": agent_name,
                "query_embedding": query["embedding"],
                "top_k": 2
            })
            search_result = json.loads(result[0].text)
            print(f"Found {search_result['result_count']} results:")
            for i, memory_text in enumerate(search_result['results'][:2]):
                print(f"  {i+1}. {memory_text}")


async def demonstrate_search_and_summarization():
    """Demonstrate search and summarization capabilities."""
    print("\n=== Search and Summarization ===")
    
    async with Client(mcp) as client:
        # Web search
        print("Performing web search...")
        result = await client.call_tool("perform_web_search", {
            "query": "Legion agent system architecture",
            "sources": ["web", "documentation", "github"]
        })
        search_result = json.loads(result[0].text)
        print(f"Search query: {search_result['query']}")
        print(f"Sources: {search_result['sources']}")
        print(f"Results found: {search_result['result_count']}")
        for i, result_text in enumerate(search_result['results'][:2]):
            print(f"  {i+1}. {result_text}")
        
        # Content summarization
        long_content = """
        The Legion agent system is a sophisticated multi-agent framework designed to handle
        complex distributed tasks through intelligent orchestration and coordination. The system
        consists of several key components including the orchestration layer, agent layer, skill
        and utility layer, persistence layer, integration layer, presentation layer, and
        infrastructure layer. Each layer serves a specific purpose in the overall architecture,
        with the orchestration layer acting as the central brain that coordinates all agent
        activities. Agents in the system have persistent memory capabilities, allowing them to
        maintain state and context across multiple interactions. The skill layer provides
        reusable functionality that can be shared across multiple agents, while the persistence
        layer ensures that all important data and state information is properly stored and
        retrievable. The integration layer handles external system connections, particularly
        with Discord for user interactions, and the presentation layer provides web-based
        interfaces for monitoring and control. Finally, the infrastructure layer manages
        deployment, monitoring, and maintenance operations to keep the entire system running
        smoothly and efficiently.
        """
        
        print(f"\nSummarizing content ({len(long_content)} characters)...")
        result = await client.call_tool("summarize_content", {
            "text": long_content,
            "max_length": 200
        })
        summary_result = json.loads(result[0].text)
        print(f"Original length: {summary_result['original_length']}")
        print(f"Summary length: {summary_result['summary_length']}")
        print(f"Compression ratio: {summary_result['compression_ratio']:.2f}")
        print(f"Summary: {summary_result['summary']}")


async def demonstrate_system_status_and_resources():
    """Demonstrate system status monitoring and resource access."""
    print("\n=== System Status and Resources ===")
    
    async with Client(mcp) as client:
        # Get system status
        print("Getting Legion system status...")
        result = await client.call_tool("get_legion_system_status", {})
        status = json.loads(result[0].text)
        print(f"MCP Server: {status['mcp_server']}")
        print(f"Memory System: {status['memory_system']}")
        print(f"Available Skills: {', '.join(status['skills'].keys())}")
        print(f"Detected Agents: {status.get('agent_count', 0)}")
        
        # Access resources
        print("\nAccessing system resources...")
        try:
            # List available resources
            resources = await client.list_resources()
            print(f"Available resources: {len(resources)}")
            for resource in resources[:3]:  # Show first 3
                print(f"  - {resource.uri}")
            
            # Access system status resource
            content = await client.read_resource("legion://system/status")
            if content:
                status_data = json.loads(content[0].text)
                print(f"System status from resource: {status_data.get('mcp_server', 'unknown')}")
        except Exception as e:
            print(f"Resource access note: {e}")


async def demonstrate_prompts():
    """Demonstrate prompt generation capabilities."""
    print("\n=== Prompt Generation ===")
    
    async with Client(mcp) as client:
        # List available prompts
        prompts = await client.list_prompts()
        print(f"Available prompts: {len(prompts)}")
        for prompt in prompts:
            print(f"  - {prompt.name}: {prompt.description}")
        
        # Generate agent diagnosis prompt
        print(f"\nGenerating agent diagnosis prompt...")
        prompt_content = await client.get_prompt("agent_diagnosis", {
            "agent_name": "demo_agent",
            "symptoms": "High memory usage, slow response times, occasional timeouts"
        })
        
        if prompt_content:
            # Handle the GetPromptResult object
            content = prompt_content.messages[0].content.text if hasattr(prompt_content, 'messages') else str(prompt_content)
            print("Generated prompt preview:")
            lines = content.split('\n')[:8]
            for line in lines:
                print(f"  {line}")
            print("  ...")
        
        # Generate system health check prompt
        print(f"\nGenerating system health check prompt...")
        prompt_content = await client.get_prompt("system_health_check", {})
        
        if prompt_content:
            # Handle the GetPromptResult object
            content = prompt_content.messages[0].content.text if hasattr(prompt_content, 'messages') else str(prompt_content)
            print("Health check prompt preview:")
            lines = content.split('\n')[:6]
            for line in lines:
                print(f"  {line}")
            print("  ...")


async def main():
    """Run all demonstration examples."""
    print("🚀 Legion MCP Server Demonstration")
    print("=" * 50)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        await demonstrate_agent_memory_operations()
        await demonstrate_task_logging()
        await demonstrate_document_management()
        await demonstrate_vector_memory_search()
        await demonstrate_search_and_summarization()
        await demonstrate_system_status_and_resources()
        await demonstrate_prompts()
        
        print("\n" + "=" * 50)
        print("✅ All demonstrations completed successfully!")
        print("\nThe Legion MCP server provides comprehensive access to:")
        print("  • Agent memory management")
        print("  • Task logging and history")
        print("  • Document storage with versioning")
        print("  • Vector-based memory search")
        print("  • Web search and content summarization")
        print("  • System status monitoring")
        print("  • Interactive prompt generation")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 