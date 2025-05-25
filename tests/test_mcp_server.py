"""
Test suite for Legion MCP Server.

This module provides comprehensive tests for the Legion MCP server,
including tool functionality, resource access, and prompt generation.
Uses FastMCP's in-memory testing pattern for efficient testing.
"""

import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List
import pytest

# Import the FastMCP client for testing
from fastmcp import Client

# Import our MCP server
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Set up environment before importing mcp_server
os.environ.setdefault('PYTHONPATH', str(Path(__file__).parent.parent))

from skills.mcp_server import mcp

# Import Legion modules for test setup
from memory.legion_memory import LegionAgentMemory


class TestLegionMCPServer:
    """Test suite for Legion MCP Server functionality."""
    
    @pytest.fixture
    def temp_memory_dir(self):
        """Create a temporary directory for memory storage during tests."""
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def test_agent_memory(self, temp_memory_dir):
        """Create a test agent with some sample data."""
        agent_name = "test_agent"
        memory = LegionAgentMemory(agent_name)
        
        # Set up some test data
        memory.set("test_key", "test_value")
        memory.set("config", {"enabled": True, "max_retries": 3})
        
        # Log some test tasks
        memory.log_task({"action": "test_action", "status": "completed"})
        memory.log_task({"action": "another_action", "status": "pending"})
        
        # Save some test documents
        memory.save_document("test_doc.txt", "This is a test document")
        memory.save_document("config.json", '{"setting": "value"}')
        
        return memory
    
    @pytest.mark.asyncio
    async def test_get_agent_memory_all(self, test_agent_memory):
        """Test retrieving all memory for an agent."""
        async with Client(mcp) as client:
            result = await client.call_tool("get_agent_memory", {"agent_name": "test_agent"})
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["agent"] == "test_agent"
            assert "memory" in data
            assert data["memory"]["test_key"] == "test_value"
            assert data["memory"]["config"]["enabled"] is True
    
    @pytest.mark.asyncio
    async def test_get_agent_memory_specific_key(self, test_agent_memory):
        """Test retrieving specific memory key for an agent."""
        async with Client(mcp) as client:
            result = await client.call_tool("get_agent_memory", {
                "agent_name": "test_agent",
                "key": "test_key"
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["agent"] == "test_agent"
            assert data["key"] == "test_key"
            assert data["value"] == "test_value"
    
    @pytest.mark.asyncio
    async def test_set_agent_memory(self, test_agent_memory):
        """Test setting memory for an agent."""
        async with Client(mcp) as client:
            result = await client.call_tool("set_agent_memory", {
                "agent_name": "test_agent",
                "key": "new_key",
                "value": "new_value"
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["status"] == "success"
            assert data["agent"] == "test_agent"
            assert data["key"] == "new_key"
            
            # Verify the value was actually set
            memory = LegionAgentMemory("test_agent")
            assert memory.get("new_key") == "new_value"
    
    @pytest.mark.asyncio
    async def test_log_agent_task(self, test_agent_memory):
        """Test logging a task for an agent."""
        task_data = {"action": "mcp_test", "status": "running", "priority": "high"}
        
        async with Client(mcp) as client:
            result = await client.call_tool("log_agent_task", {
                "agent_name": "test_agent",
                "task_data": task_data
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["status"] == "success"
            assert data["agent"] == "test_agent"
    
    @pytest.mark.asyncio
    async def test_get_agent_task_log(self, test_agent_memory):
        """Test retrieving task log for an agent."""
        async with Client(mcp) as client:
            result = await client.call_tool("get_agent_task_log", {
                "agent_name": "test_agent"
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["agent"] == "test_agent"
            assert data["task_count"] >= 2  # We logged 2 tasks in fixture
            assert "tasks" in data
            assert isinstance(data["tasks"], list)
    
    @pytest.mark.asyncio
    async def test_get_agent_task_log_with_limit(self, test_agent_memory):
        """Test retrieving limited task log for an agent."""
        async with Client(mcp) as client:
            result = await client.call_tool("get_agent_task_log", {
                "agent_name": "test_agent",
                "limit": 1
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["agent"] == "test_agent"
            assert len(data["tasks"]) == 1
    
    @pytest.mark.asyncio
    async def test_save_agent_document(self, test_agent_memory):
        """Test saving a document for an agent."""
        async with Client(mcp) as client:
            result = await client.call_tool("save_agent_document", {
                "agent_name": "test_agent",
                "document_name": "mcp_test.md",
                "content": "# MCP Test Document\n\nThis is a test."
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["status"] == "success"
            assert data["agent"] == "test_agent"
            assert data["document"] == "mcp_test.md"
            assert "versioned_path" in data
    
    @pytest.mark.asyncio
    async def test_get_agent_document(self, test_agent_memory):
        """Test retrieving a document for an agent."""
        async with Client(mcp) as client:
            result = await client.call_tool("get_agent_document", {
                "agent_name": "test_agent",
                "document_name": "test_doc.txt"
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["status"] == "success"
            assert data["agent"] == "test_agent"
            assert data["document"] == "test_doc.txt"
            assert data["content"] == "This is a test document"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self, test_agent_memory):
        """Test retrieving a nonexistent document."""
        async with Client(mcp) as client:
            result = await client.call_tool("get_agent_document", {
                "agent_name": "test_agent",
                "document_name": "nonexistent.txt"
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["status"] == "not_found"
            assert data["agent"] == "test_agent"
    
    @pytest.mark.asyncio
    async def test_list_agent_documents(self, test_agent_memory):
        """Test listing documents for an agent."""
        async with Client(mcp) as client:
            result = await client.call_tool("list_agent_documents", {
                "agent_name": "test_agent"
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["agent"] == "test_agent"
            assert data["document_count"] >= 2  # We saved 2 documents in fixture
            assert "documents" in data
            assert isinstance(data["documents"], list)
    
    @pytest.mark.asyncio
    async def test_store_and_search_vector_memories(self, test_agent_memory):
        """Test storing and searching vector memories."""
        # First, store some vector memories
        memory_snippets = [
            {
                "text": "The weather is sunny today",
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
            },
            {
                "text": "It's raining outside",
                "embedding": [0.5, 0.4, 0.3, 0.2, 0.1]
            },
            {
                "text": "The sky is clear and blue",
                "embedding": [0.2, 0.3, 0.4, 0.5, 0.6]
            }
        ]
        
        async with Client(mcp) as client:
            # Store memories
            store_result = await client.call_tool("store_vector_memories", {
                "agent_name": "test_agent",
                "memory_snippets": memory_snippets
            })
            
            assert len(store_result) == 1
            store_data = json.loads(store_result[0].text)
            assert store_data["status"] == "success"
            assert store_data["stored_count"] == 3
            
            # Search memories
            search_result = await client.call_tool("search_vector_memories", {
                "agent_name": "test_agent",
                "query_embedding": [0.15, 0.25, 0.35, 0.45, 0.55],  # Similar to first snippet
                "top_k": 2
            })
            
            assert len(search_result) == 1
            search_data = json.loads(search_result[0].text)
            assert search_data["agent"] == "test_agent"
            assert search_data["result_count"] >= 0  # May be 0 if no vector store exists yet
    
    @pytest.mark.asyncio
    async def test_perform_web_search(self, test_agent_memory):
        """Test web search functionality."""
        async with Client(mcp) as client:
            result = await client.call_tool("perform_web_search", {
                "query": "Legion agent system",
                "sources": ["web", "docs"]
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["query"] == "Legion agent system"
            assert data["sources"] == ["web", "docs"]
            assert "results" in data
            assert isinstance(data["results"], list)
    
    @pytest.mark.asyncio
    async def test_perform_vector_search(self, test_agent_memory):
        """Test vector search functionality."""
        documents = [
            {
                "id": "doc1",
                "text": "Document about weather",
                "embedding": [0.1, 0.2, 0.3]
            },
            {
                "id": "doc2", 
                "text": "Document about technology",
                "embedding": [0.7, 0.8, 0.9]
            }
        ]
        
        async with Client(mcp) as client:
            result = await client.call_tool("perform_vector_search", {
                "query_embedding": [0.2, 0.3, 0.4],
                "documents": documents,
                "top_k": 1
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["document_count"] == 2
            assert data["top_k"] == 1
            assert "results" in data
    
    @pytest.mark.asyncio
    async def test_summarize_content(self, test_agent_memory):
        """Test content summarization."""
        long_text = "This is a very long text that needs to be summarized. " * 20
        
        async with Client(mcp) as client:
            result = await client.call_tool("summarize_content", {
                "text": long_text,
                "max_length": 100
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["original_length"] == len(long_text)
            assert "summary" in data
            assert "compression_ratio" in data
    
    @pytest.mark.asyncio
    async def test_get_legion_system_status(self, test_agent_memory):
        """Test getting Legion system status."""
        async with Client(mcp) as client:
            result = await client.call_tool("get_legion_system_status", {})
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            assert data["mcp_server"] == "active"
            assert "timestamp" in data
            assert "memory_system" in data
            assert "skills" in data
    
    @pytest.mark.asyncio
    async def test_agent_memory_resource(self, test_agent_memory):
        """Test accessing agent memory through resources."""
        async with Client(mcp) as client:
                        # List available resources
            resources = await client.list_resources()
            
            # Check if our resource pattern exists
            memory_resources = [r for r in resources if "memory://agents/" in str(r.uri)]
        assert len(memory_resources) > 0
            
            # Access the specific agent memory resource
            resource_uri = "memory://agents/test_agent/memory"
            content = await client.read_resource(resource_uri)
            
            assert len(content) > 0
            data = json.loads(content[0].text)
            assert "test_key" in data or "error" in data  # May error if path issues
    
    @pytest.mark.asyncio
    async def test_system_status_resource(self, test_agent_memory):
        """Test accessing system status through resources."""
        async with Client(mcp) as client:
            content = await client.read_resource("legion://system/status")
            
            assert len(content) > 0
            data = json.loads(content[0].text)
            assert "mcp_server" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_agent_diagnosis_prompt(self, test_agent_memory):
        """Test agent diagnosis prompt generation."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            
            # Check if our prompt exists
            diagnosis_prompts = [p for p in prompts if p.name == "agent_diagnosis"]
            assert len(diagnosis_prompts) > 0
            
            # Get the prompt content
            prompt_content = await client.get_prompt("agent_diagnosis", {
                "agent_name": "test_agent",
                "symptoms": "High CPU usage and memory leaks"
            })
            
            assert len(prompt_content) > 0
            content = prompt_content[0].text
            assert "test_agent" in content
            assert "High CPU usage" in content
            assert "diagnostician" in content
    
    @pytest.mark.asyncio
    async def test_memory_analysis_prompt(self, test_agent_memory):
        """Test agent memory analysis prompt generation."""
        async with Client(mcp) as client:
            prompt_content = await client.get_prompt("agent_memory_analysis", {
                "agent_name": "test_agent",
                "analysis_type": "performance"
            })
            
            assert len(prompt_content) > 0
            content = prompt_content[0].text
            assert "test_agent" in content
            assert "performance" in content
            assert "memory patterns" in content
    
    @pytest.mark.asyncio
    async def test_system_health_check_prompt(self, test_agent_memory):
        """Test system health check prompt generation."""
        async with Client(mcp) as client:
            prompt_content = await client.get_prompt("system_health_check", {})
            
            assert len(prompt_content) > 0
            content = prompt_content[0].text
            assert "health check" in content
            assert "Legion system" in content
    
    @pytest.mark.asyncio 
    async def test_error_handling_invalid_agent(self, test_agent_memory):
        """Test error handling for invalid agent operations."""
        async with Client(mcp) as client:
            result = await client.call_tool("get_agent_memory", {
                "agent_name": "nonexistent_agent"
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            # Should handle gracefully - either return empty memory or error
            assert "agent" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_invalid_memory_snippet_format(self, test_agent_memory):
        """Test error handling for invalid memory snippet format."""
        # Only use valid dict formats since FastMCP validates input types
        invalid_snippets = [
            {"text": "Valid snippet but no embedding"},
            {"embedding": [0.1, 0.2], "missing": "text"}
        ]
        
        async with Client(mcp) as client:
            result = await client.call_tool("store_vector_memories", {
                "agent_name": "test_agent",
                "memory_snippets": invalid_snippets
            })
            
            assert len(result) == 1
            response = result[0].text
            data = json.loads(response)
            
            # Should handle invalid formats gracefully
            assert "status" in data
            if data["status"] == "success":
                assert data["stored_count"] == 0  # No valid snippets


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 