"""
Legion MCP Server - Model Context Protocol integration for Legion agent system.

This module provides a FastMCP server that exposes Legion's core functionality
through MCP tools, resources, and prompts. It enables LLM applications to
interact with Legion agents, memory systems, and search capabilities.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add the parent directory to the path to import Legion modules
sys.path.append(str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from fastmcp.resources import Resource
from fastmcp.prompts import Prompt

# Legion imports
from memory.legion_memory import LegionAgentMemory
from skills.search import search_placeholder, search_web
from skills.summarize import summarize_texts
from skills.llm_client import get_llm_client

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP("Legion MCP Server")


@mcp.tool()
def get_agent_memory(agent_name: str, key: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve memory data for a specific Legion agent.
    
    Args:
        agent_name: Name of the agent
        key: Optional specific key to retrieve (if None, returns all memory)
    
    Returns:
        Dictionary containing the requested memory data
    """
    try:
        memory = LegionAgentMemory(agent_name)
        if key:
            value = memory.get(key)
            return {"agent": agent_name, "key": key, "value": value}
        else:
            # Return all memory data
            return {"agent": agent_name, "memory": memory._data}
    except Exception as e:
        logger.error(f"Error retrieving memory for agent {agent_name}: {e}")
        return {"error": f"Failed to retrieve memory: {str(e)}"}


@mcp.tool()
def set_agent_memory(agent_name: str, key: str, value: Any) -> Dict[str, str]:
    """
    Set memory data for a specific Legion agent.
    
    Args:
        agent_name: Name of the agent
        key: Memory key to set
        value: Value to store
    
    Returns:
        Status message indicating success or failure
    """
    try:
        memory = LegionAgentMemory(agent_name)
        memory.set(key, value)
        return {
            "status": "success",
            "message": f"Set {key} for agent {agent_name}",
            "agent": agent_name,
            "key": key
        }
    except Exception as e:
        logger.error(f"Error setting memory for agent {agent_name}: {e}")
        return {"status": "error", "message": f"Failed to set memory: {str(e)}"}


@mcp.tool()
def log_agent_task(agent_name: str, task_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Log a task for a specific Legion agent.
    
    Args:
        agent_name: Name of the agent
        task_data: Task information to log
    
    Returns:
        Status message indicating success or failure
    """
    try:
        memory = LegionAgentMemory(agent_name)
        # Add timestamp to task data
        enriched_task = {
            **task_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "logged_via": "mcp_server"
        }
        memory.log_task(enriched_task)
        return {
            "status": "success",
            "message": f"Logged task for agent {agent_name}",
            "agent": agent_name
        }
    except Exception as e:
        logger.error(f"Error logging task for agent {agent_name}: {e}")
        return {"status": "error", "message": f"Failed to log task: {str(e)}"}


@mcp.tool()
def get_agent_task_log(agent_name: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Retrieve task log for a specific Legion agent.
    
    Args:
        agent_name: Name of the agent
        limit: Optional limit on number of tasks to return (most recent first)
    
    Returns:
        Dictionary containing the agent's task log
    """
    try:
        memory = LegionAgentMemory(agent_name)
        tasks = memory.get_task_log()
        
        # Sort by timestamp if available, most recent first
        def get_timestamp(task):
            if isinstance(task, dict) and "timestamp" in task:
                return task["timestamp"]
            return "1970-01-01T00:00:00+00:00"  # fallback for old entries
        
        tasks.sort(key=get_timestamp, reverse=True)
        
        if limit:
            tasks = tasks[:limit]
            
        return {
            "agent": agent_name,
            "task_count": len(tasks),
            "tasks": tasks
        }
    except Exception as e:
        logger.error(f"Error retrieving task log for agent {agent_name}: {e}")
        return {"error": f"Failed to retrieve task log: {str(e)}"}


@mcp.tool()
def save_agent_document(agent_name: str, document_name: str, content: str) -> Dict[str, str]:
    """
    Save a document for a specific Legion agent with versioning.
    
    Args:
        agent_name: Name of the agent
        document_name: Name of the document
        content: Document content
    
    Returns:
        Status message with the versioned file path
    """
    try:
        memory = LegionAgentMemory(agent_name)
        versioned_path = memory.save_document(document_name, content)
        return {
            "status": "success",
            "message": f"Saved document {document_name} for agent {agent_name}",
            "agent": agent_name,
            "document": document_name,
            "versioned_path": versioned_path
        }
    except Exception as e:
        logger.error(f"Error saving document for agent {agent_name}: {e}")
        return {"status": "error", "message": f"Failed to save document: {str(e)}"}


@mcp.tool()
def get_agent_document(agent_name: str, document_name: str, version: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve a document for a specific Legion agent.
    
    Args:
        agent_name: Name of the agent
        document_name: Name of the document
        version: Optional version identifier (timestamp)
    
    Returns:
        Dictionary containing the document content
    """
    try:
        memory = LegionAgentMemory(agent_name)
        content = memory.get_document(document_name, version)
        if content is None:
            return {
                "status": "not_found",
                "message": f"Document {document_name} not found for agent {agent_name}",
                "agent": agent_name,
                "document": document_name
            }
        return {
            "status": "success",
            "agent": agent_name,
            "document": document_name,
            "version": version,
            "content": content
        }
    except Exception as e:
        logger.error(f"Error retrieving document for agent {agent_name}: {e}")
        return {"error": f"Failed to retrieve document: {str(e)}"}


@mcp.tool()
def list_agent_documents(agent_name: str) -> Dict[str, Any]:
    """
    List all documents for a specific Legion agent.
    
    Args:
        agent_name: Name of the agent
    
    Returns:
        Dictionary containing the list of documents
    """
    try:
        memory = LegionAgentMemory(agent_name)
        documents = memory.list_documents()
        return {
            "agent": agent_name,
            "document_count": len(documents),
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Error listing documents for agent {agent_name}: {e}")
        return {"error": f"Failed to list documents: {str(e)}"}


@mcp.tool()
def search_vector_memories(
    agent_name: str, 
    query_embedding: List[float], 
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Search vector memories for a specific Legion agent using embedding similarity.
    
    Args:
        agent_name: Name of the agent
        query_embedding: Query vector embedding
        top_k: Number of top results to return
    
    Returns:
        Dictionary containing the search results
    """
    try:
        results = LegionAgentMemory.retrieve_memories(agent_name, query_embedding, top_k)
        return {
            "agent": agent_name,
            "query_embedding_size": len(query_embedding),
            "top_k": top_k,
            "result_count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error searching memories for agent {agent_name}: {e}")
        return {"error": f"Failed to search memories: {str(e)}"}


@mcp.tool()
def store_vector_memories(
    agent_name: str, 
    memory_snippets: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Store vector memories for a specific Legion agent.
    
    Args:
        agent_name: Name of the agent
        memory_snippets: List of memory snippets with 'text' and 'embedding' keys
    
    Returns:
        Status message indicating success or failure
    """
    try:
        # Validate snippets format
        valid_snippets = []
        for snippet in memory_snippets:
            if isinstance(snippet, dict) and "text" in snippet and "embedding" in snippet:
                valid_snippets.append(snippet)
            else:
                logger.warning(f"Invalid snippet format: {snippet}")
        
        LegionAgentMemory.store_memories(agent_name, valid_snippets)
        return {
            "status": "success",
            "message": f"Stored {len(valid_snippets)} memory snippets for agent {agent_name}",
            "agent": agent_name,
            "stored_count": len(valid_snippets),
            "total_provided": len(memory_snippets)
        }
    except Exception as e:
        logger.error(f"Error storing memories for agent {agent_name}: {e}")
        return {"status": "error", "message": f"Failed to store memories: {str(e)}"}


@mcp.tool()
def perform_web_search(query: str, sources: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Perform a web search using Legion's search skill.
    
    Args:
        query: Search query string
        sources: Optional list of sources to search
    
    Returns:
        Dictionary containing search results
    """
    try:
        if sources is None:
            sources = ["web"]
        
        results = search_web(query, sources)
        return {
            "query": query,
            "sources": sources,
            "result_count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error performing web search: {e}")
        return {"error": f"Failed to perform search: {str(e)}"}


@mcp.tool()
def perform_vector_search(
    query_embedding: List[float],
    documents: List[Dict[str, Any]],
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Perform vector similarity search over provided documents.
    
    Args:
        query_embedding: Query vector embedding
        documents: List of documents with 'embedding' key
        top_k: Number of top results to return
    
    Returns:
        Dictionary containing search results
    """
    try:
        results = search_placeholder(query_embedding, documents, top_k)
        return {
            "query_embedding_size": len(query_embedding),
            "document_count": len(documents),
            "top_k": top_k,
            "result_count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error performing vector search: {e}")
        return {"error": f"Failed to perform vector search: {str(e)}"}


@mcp.tool()
def summarize_content(text: str, max_length: Optional[int] = None) -> Dict[str, Any]:
    """
    Summarize text content using Legion's summarization skill.
    
    Args:
        text: Text content to summarize
        max_length: Optional maximum length for the summary
    
    Returns:
        Dictionary containing the summary
    """
    try:
        if max_length is None:
            max_length = len(text) // 3  # Default to 1/3 of original length
        
        # Use LLM client for better summarization
        llm_client = get_llm_client()
        summary = llm_client.summarize_text(text, max_length)
        return {
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text) if text else 0,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error summarizing content: {e}")
        return {"error": f"Failed to summarize content: {str(e)}"}


@mcp.tool()
def ask_llm(
    prompt: str, 
    system_message: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Ask the configured LLM a question or to complete a task.
    
    Args:
        prompt: The prompt or question to send to the LLM
        system_message: Optional system message to set context
        temperature: Optional temperature parameter for randomness (0.0-1.0)
        max_tokens: Optional maximum tokens for the response
    
    Returns:
        Dictionary containing the LLM response and metadata
    """
    try:
        llm_client = get_llm_client()
        
        # Add system message to prompt if provided
        if system_message:
            full_prompt = f"System: {system_message}\n\nUser: {prompt}"
        else:
            full_prompt = prompt
        
        # Build kwargs for the LLM call
        llm_kwargs = {}
        if temperature is not None:
            llm_kwargs["temperature"] = temperature
        if max_tokens is not None:
            llm_kwargs["max_tokens"] = max_tokens
        
        response = llm_client.complete_text(full_prompt, **llm_kwargs)
        
        return {
            "prompt": prompt,
            "system_message": system_message,
            "response": response,
            "provider": llm_client.provider,
            "parameters": llm_kwargs,
            "success": True
        }
    except Exception as e:
        logger.error(f"Error asking LLM: {e}")
        return {"error": f"Failed to get LLM response: {str(e)}", "success": False}


@mcp.tool()
def diagnose_agent_with_llm(
    agent_name: str, 
    symptoms: str, 
    include_memory: bool = True,
    include_tasks: bool = True
) -> Dict[str, Any]:
    """
    Diagnose agent issues using LLM analysis of symptoms and agent data.
    
    Args:
        agent_name: Name of the agent to diagnose
        symptoms: Description of the symptoms or issues
        include_memory: Whether to include agent memory in the analysis
        include_tasks: Whether to include recent tasks in the analysis
    
    Returns:
        Dictionary containing the diagnosis and recommendations
    """
    try:
        llm_client = get_llm_client()
        
        # Gather agent context
        context_parts = [f"Symptoms: {symptoms}"]
        
        if include_memory:
            try:
                memory = LegionAgentMemory(agent_name)
                memory_data = memory._data
                if memory_data:
                    context_parts.append(f"Agent Memory: {json.dumps(memory_data, indent=2)}")
                else:
                    context_parts.append("Agent Memory: No memory data found")
            except Exception as e:
                context_parts.append(f"Agent Memory: Failed to retrieve ({str(e)})")
        
        if include_tasks:
            try:
                memory = LegionAgentMemory(agent_name)
                tasks = memory.get_task_log()
                recent_tasks = tasks[-5:] if tasks else []  # Last 5 tasks
                if recent_tasks:
                    context_parts.append(f"Recent Tasks: {json.dumps(recent_tasks, indent=2)}")
                else:
                    context_parts.append("Recent Tasks: No task history found")
            except Exception as e:
                context_parts.append(f"Recent Tasks: Failed to retrieve ({str(e)})")
        
        context = "\n\n".join(context_parts)
        
        system_message = f"""You are a Legion system diagnostician analyzing agent '{agent_name}'. 
Provide a structured diagnosis including:
1. Problem identification and root cause analysis
2. Severity assessment (low, medium, high, critical)
3. Immediate remediation steps
4. Long-term prevention strategies
5. Monitoring recommendations

Be specific and actionable in your recommendations."""
        
        diagnosis = llm_client.complete_text(context, max_tokens=1000, temperature=0.1)
        
        return {
            "agent": agent_name,
            "symptoms": symptoms,
            "diagnosis": diagnosis,
            "context_included": {
                "memory": include_memory,
                "tasks": include_tasks
            },
            "provider": llm_client.provider,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error diagnosing agent {agent_name}: {e}")
        return {"error": f"Failed to diagnose agent: {str(e)}", "success": False}


@mcp.tool()
def analyze_agent_performance_with_llm(
    agent_name: str,
    analysis_type: str = "comprehensive",
    time_window_hours: int = 24
) -> Dict[str, Any]:
    """
    Analyze agent performance using LLM analysis of agent data and patterns.
    
    Args:
        agent_name: Name of the agent to analyze
        analysis_type: Type of analysis (comprehensive, memory, tasks, performance)
        time_window_hours: Time window for analysis in hours
    
    Returns:
        Dictionary containing the performance analysis and recommendations
    """
    try:
        llm_client = get_llm_client()
        memory = LegionAgentMemory(agent_name)
        
        # Gather comprehensive agent data
        analysis_data = {
            "agent_name": agent_name,
            "memory_data": memory._data,
            "task_history": memory.get_task_log(),
            "documents": memory.list_documents(),
            "analysis_type": analysis_type,
            "time_window_hours": time_window_hours
        }
        
        # Create analysis prompt based on type
        if analysis_type == "memory":
            focus = "memory usage patterns, data growth, and optimization opportunities"
        elif analysis_type == "tasks":
            focus = "task execution patterns, success rates, and performance trends"
        elif analysis_type == "performance":
            focus = "overall performance metrics, bottlenecks, and efficiency"
        else:  # comprehensive
            focus = "all aspects of agent performance including memory, tasks, and overall efficiency"
        
        system_message = f"""You are a Legion system performance analyst. Analyze the agent data focusing on {focus}.
Provide insights about:
1. Current performance status
2. Identified patterns and trends
3. Performance bottlenecks or issues
4. Optimization recommendations
5. Capacity planning suggestions

Be data-driven and provide specific, actionable recommendations."""
        
        context = f"Agent Analysis Data:\n{json.dumps(analysis_data, indent=2, default=str)}"
        
        analysis = llm_client.complete_text(context, max_tokens=1500, temperature=0.1)
        
        return {
            "agent": agent_name,
            "analysis_type": analysis_type,
            "time_window_hours": time_window_hours,
            "analysis": analysis,
            "data_summary": {
                "memory_keys": len(analysis_data["memory_data"]),
                "task_count": len(analysis_data["task_history"]),
                "document_count": len(analysis_data["documents"])
            },
            "provider": llm_client.provider,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error analyzing agent {agent_name}: {e}")
        return {"error": f"Failed to analyze agent: {str(e)}", "success": False}


@mcp.tool()
def get_llm_status() -> Dict[str, Any]:
    """
    Get the current status of the LLM client and provider.
    
    Returns:
        Dictionary containing LLM client status and configuration
    """
    try:
        llm_client = get_llm_client()
        status = llm_client.get_status()
        
        return {
            "llm_available": True,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting LLM status: {e}")
        return {
            "llm_available": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@mcp.tool()
def get_legion_system_status() -> Dict[str, Any]:
    """
    Get the current status of the Legion system.
    
    Returns:
        Dictionary containing system status information
    """
    try:
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mcp_server": "active",
            "memory_system": "available",
            "skills": {
                "search": "available",
                "summarize": "available",
                "vector_search": "available"
            }
        }
        
        # Add LLM status
        try:
            llm_client = get_llm_client()
            llm_status = llm_client.get_status()
            status["llm"] = {
                "provider": llm_status["provider"],
                "available": llm_status["client_initialized"],
                "config_keys": list(llm_status["config"].keys()) if llm_status["config"] else []
            }
        except Exception as e:
            status["llm"] = {
                "provider": "unknown",
                "available": False,
                "error": str(e)
            }
        
        # Check if memory directory exists
        memory_dir = Path("memory")
        if memory_dir.exists():
            status["memory_directory"] = "exists"
            # Count agent memory directories
            agent_dirs = [d for d in memory_dir.iterdir() if d.is_dir()]
            status["agent_count"] = len(agent_dirs)
            status["agents"] = [d.name for d in agent_dirs]
        else:
            status["memory_directory"] = "missing"
            status["agent_count"] = 0
            status["agents"] = []
        
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {"error": f"Failed to get system status: {str(e)}"}


# Resources - expose Legion system data
@mcp.resource("memory://agents/{agent_name}/memory")
async def agent_memory_resource(agent_name: str) -> str:
    """Resource to access agent memory data."""
    try:
        memory = LegionAgentMemory(agent_name)
        return json.dumps(memory._data, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to load memory: {str(e)}"})


@mcp.resource("memory://agents/{agent_name}/tasks")
async def agent_tasks_resource(agent_name: str) -> str:
    """Resource to access agent task logs."""
    try:
        memory = LegionAgentMemory(agent_name)
        tasks = memory.get_task_log()
        return json.dumps(tasks, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to load tasks: {str(e)}"})


@mcp.resource("memory://agents/{agent_name}/documents")
async def agent_documents_resource(agent_name: str) -> str:
    """Resource to access agent document list."""
    try:
        memory = LegionAgentMemory(agent_name)
        documents = memory.list_documents()
        return json.dumps({"documents": documents}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to load documents: {str(e)}"})


@mcp.resource("legion://system/status")
async def system_status_resource() -> str:
    """Resource to access Legion system status."""
    try:
        status = get_legion_system_status()
        return json.dumps(status, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get system status: {str(e)}"})


# Prompts - predefined interaction patterns
@mcp.prompt("agent_diagnosis")
async def agent_diagnosis_prompt(agent_name: str, symptoms: str) -> str:
    """Prompt for diagnosing agent issues using Legion's doctor agent pattern."""
    return f"""
You are a Legion system diagnostician. Analyze the following symptoms for agent '{agent_name}':

Symptoms: {symptoms}

Please provide a structured diagnosis including:
1. Likely root cause
2. Severity level (low, medium, high, critical)
3. Recommended remediation steps
4. Prevention strategies

Use the Legion agent memory and task logs to inform your analysis.
Available tools: get_agent_memory, get_agent_task_log, get_legion_system_status
"""


@mcp.prompt("agent_memory_analysis")
async def agent_memory_analysis_prompt(agent_name: str, analysis_type: str = "summary") -> str:
    """Prompt for analyzing agent memory patterns."""
    return f"""
You are analyzing the memory patterns for Legion agent '{agent_name}'.

Analysis type: {analysis_type}

Please examine the agent's memory, task history, and documents to provide insights about:
1. Memory usage patterns
2. Task execution trends
3. Document storage behavior
4. Potential optimization opportunities

Use these tools to gather data:
- get_agent_memory
- get_agent_task_log
- list_agent_documents
- get_legion_system_status

Provide actionable recommendations for improving agent performance.
"""


@mcp.prompt("system_health_check")
async def system_health_check_prompt() -> str:
    """Prompt for comprehensive Legion system health analysis."""
    return """
Perform a comprehensive health check of the Legion system.

Analyze the following aspects:
1. System status and availability
2. Agent memory health across all agents
3. Task execution patterns
4. Resource utilization
5. Potential issues or bottlenecks

Use these tools:
- get_legion_system_status
- get_agent_memory (for each discovered agent)
- get_agent_task_log (for each discovered agent)

Provide a structured health report with recommendations for optimization or issue resolution.
"""


def run_server(host: str = "localhost", port: int = 8765) -> None:
    """
    Run the Legion MCP server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"Starting Legion MCP Server on {host}:{port}")
    
    # Run the server
    try:
        import uvicorn
        uvicorn.run(mcp, host=host, port=port)
    except ImportError:
        # Fallback to basic asyncio server
        logger.warning("uvicorn not available, using basic server")
        asyncio.run(mcp.run())


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Legion MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind to")
    args = parser.parse_args()
    
    run_server(args.host, args.port) 