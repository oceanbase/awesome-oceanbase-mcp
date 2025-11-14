#!/usr/bin/env python
# -*- coding: UTF-8 -*
"""
PowerMem MCP Server

MCP server based on FastMCP framework, supporting three transport methods: stdio, sse, and streamable-http
Provides 7 core tools for memory management
"""

import sys
from typing import Optional, Dict, Any, List, Union
from fastmcp import FastMCP
from powermem import create_memory
import json



# ============================================================================
# Part 1: MCP Server
# ============================================================================

# Create FastMCP instance
mcp = FastMCP("PowerMem MCP Server")

# Global Memory instance (lazy initialization)
_memory_instance = None


def get_memory():
    """
    Get or create Memory instance

    Uses singleton pattern, automatically loads configuration from .env and creates Memory instance on first call
    Similar to run_obdiag_command function in obdiag example, encapsulates underlying operations

    create_memory() will automatically call auto_config() to load configuration, searches for .env files in:
    1. Current working directory's .env
    2. Project root directory's .env
    3. examples/configs/.env
    """
    global _memory_instance
    if _memory_instance is None:
        # create_memory() will automatically call auto_config() to load configuration
        _memory_instance = create_memory()
    return _memory_instance


def format_memories_for_llm(memories: Dict[str, Any]) -> str:
    """
    Format memory results as JSON string for LLM processing

    Args:
        memories: Memory result dictionary, containing results and optional relations fields

    Returns:
        JSON formatted string
    """
    return json.dumps(memories, ensure_ascii=False, indent=2)


# ============================================================================
# Part 2: MCP Tools (7 core tools)
# ============================================================================

@mcp.tool()
def add_memory(
        messages: Union[str, Dict, List[Dict]],
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        infer: bool = True
) -> str:
    """
    Add new memory to storage

    Args:
        messages: Memory content, can be string, message dict, or message list
        user_id: User identifier
        agent_id: Agent identifier
        run_id: Run/session identifier
        metadata: Metadata dictionary
        infer: Whether to use intelligent mode (default True)

    Returns:
        JSON formatted string
    """
    memory = get_memory()
    result = memory.add(
        messages=messages,
        user_id=user_id,
        agent_id=agent_id,
        run_id=run_id,
        metadata=metadata,
        infer=infer
    )
    return format_memories_for_llm(result)


@mcp.tool()
def search_memories(
        query: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        limit: int = 10,
        threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
) -> str:
    """
    Search memories

    Args:
        query: Search query text
        user_id: User identifier
        agent_id: Agent identifier
        run_id: Run/session identifier
        limit: Maximum number of results (default 10)
        threshold: Similarity threshold (0.0-1.0)
        filters: Metadata filters

    Returns:
        JSON formatted string
    """
    memory = get_memory()
    result = memory.search(
        query=query,
        user_id=user_id,
        agent_id=agent_id,
        run_id=run_id,
        limit=limit,
        threshold=threshold,
        filters=filters
    )
    return format_memories_for_llm(result)


@mcp.tool()
def get_memory_by_id(
        memory_id: int,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None
) -> str:
    """
    Get specific memory

    Args:
        memory_id: Memory ID
        user_id: User identifier
        agent_id: Agent identifier

    Returns:
        JSON formatted string, returns error message if not found
    """
    memory = get_memory()
    result = memory.get(memory_id=memory_id, user_id=user_id, agent_id=agent_id)
    if result is None:
        return format_memories_for_llm({"error": f"Memory {memory_id} not found"})
    return format_memories_for_llm(result)


@mcp.tool()
def update_memory(
        memory_id: int,
        content: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Update memory

    Args:
        memory_id: Memory ID
        content: New content
        user_id: User identifier
        agent_id: Agent identifier
        metadata: Updated metadata

    Returns:
        JSON formatted string
    """
    memory = get_memory()
    result = memory.update(
        memory_id=memory_id,
        content=content,
        user_id=user_id,
        agent_id=agent_id,
        metadata=metadata
    )
    return format_memories_for_llm(result)


@mcp.tool()
def delete_memory(
        memory_id: int,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None
) -> str:
    """
    Delete memory

    Args:
        memory_id: Memory ID
        user_id: User identifier
        agent_id: Agent identifier

    Returns:
        JSON formatted string
    """
    memory = get_memory()
    success = memory.delete(memory_id=memory_id, user_id=user_id, agent_id=agent_id)
    return format_memories_for_llm({"success": success, "memory_id": memory_id})


@mcp.tool()
def delete_all_memories(
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None
) -> str:
    """
    Batch delete memories

    Args:
        user_id: User identifier
        agent_id: Agent identifier
        run_id: Run/session identifier

    Returns:
        JSON formatted string
    """
    memory = get_memory()
    success = memory.delete_all(user_id=user_id, agent_id=agent_id, run_id=run_id)
    return format_memories_for_llm({"success": success})


@mcp.tool()
def list_memories(
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
) -> str:
    """
    List all memories

    Args:
        user_id: User identifier
        agent_id: Agent identifier
        run_id: Run/session identifier
        limit: Maximum number of results (default 100)
        offset: Offset (default 0)
        filters: Metadata filters

    Returns:
        JSON formatted string
    """

    memory = get_memory()
    result = memory.get_all(
        user_id=user_id,
        agent_id=agent_id,
        run_id=run_id,
        limit=limit,
        offset=offset
    )
    return format_memories_for_llm(result)


# ============================================================================
# Startup function
# ============================================================================

def main():
    """
    Start MCP server

    Supports three transport methods:
    - stdio: Standard input/output (JSON-RPC)
    - sse: Server-Sent Events (HTTP SSE)
    - streamable-http: Streamable HTTP (HTTP streaming, recommended for Dify)

    Usage:
        python server.py streamable-http 8000
        python server.py sse 8000
        python server.py stdio
        powermem-mcp streamable-http 8000
    """
    # Parse command line arguments
    transport = "streamable-http"  # Default to streamable-http
    port = 8000
    path = "/mcp"

    if len(sys.argv) > 1:
        transport = sys.argv[1]  # stdio, sse, streamable-http

    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    # Start server based on transport method
    if transport == "stdio":
        print("Starting PowerMem MCP Server with stdio transport...")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print(f"Starting PowerMem MCP Server with SSE transport on port {port}...")
        mcp.run(transport="sse", host="0.0.0.0", port=port, path=path)
    else:  # streamable-http
        print(f"Starting PowerMem MCP Server with streamable-http transport on port {port}...")
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path=path)


if __name__ == "__main__":
    main()

