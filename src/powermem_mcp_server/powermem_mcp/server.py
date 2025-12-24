#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
PowerMem MCP Server

MCP server based on FastMCP framework, supporting three transport methods: stdio, sse, and streamable-http
Provides 13 tools for memory and user profile management:
- 7 core memory tools: add, search, get, update, delete, delete_all, list
- 6 user profile tools: add_with_profile, search_with_profile, get_profile, list_profiles, delete_profile, delete_memory_with_profile
"""

import sys
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date
from fastmcp import FastMCP
from powermem import create_memory, auto_config
from powermem.user_memory import UserMemory
import json

# ============================================================================
# Part 1: MCP Server
# ============================================================================

# Create FastMCP instance
mcp = FastMCP("PowerMem MCP Server")

# Global Memory instance (lazy initialization)
_memory_instance = None
_user_memory_instance = None


def get_memory():
    """
    Get or create Memory instance

    Uses singleton pattern, automatically loads configuration from .env and creates Memory instance on first call
    Similar to run_powermem_command function in powermem example, encapsulates underlying operations

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


def get_user_memory():
    """
    Get or create UserMemory instance for user profile management

    Uses singleton pattern, automatically loads configuration from .env and creates UserMemory instance on first call
    UserMemory provides additional user profile extraction and management capabilities on top of Memory.
    """
    global _user_memory_instance
    if _user_memory_instance is None:
        config = auto_config()
        _user_memory_instance = UserMemory(config=config)
    return _user_memory_instance


def convert_datetime_to_str(obj: Any) -> Any:
    """
    Recursively convert datetime and date objects to ISO format strings

    Args:
        obj: Object that may contain datetime/date objects

    Returns:
        Object with all datetime/date objects converted to strings
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_datetime_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_str(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_datetime_to_str(item) for item in obj)
    else:
        return obj


class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles datetime and date objects
    """

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def format_memories_for_llm(memories: Dict[str, Any]) -> str:
    """
    Format memory results as JSON string for LLM processing

    Args:
        memories: Memory result dictionary, containing results and optional relations fields

    Returns:
        JSON formatted string
    """
    # First convert all datetime objects recursively, then serialize
    converted_memories = convert_datetime_to_str(memories)
    return json.dumps(
        converted_memories, ensure_ascii=False, indent=2, cls=DateTimeEncoder
    )


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
    infer: bool = True,
) -> str:
    """
    Add new memory to storage

    Args:
        messages: Memory content, can be string, message dict, or message list.
            IMPORTANT: Each message dict MUST contain 'role' and 'content' fields.
        user_id: User identifier
        agent_id: Agent identifier
        run_id: Run/session identifier
        metadata: Metadata dictionary
        infer: Whether to use intelligent mode (default True)

    Returns:
        JSON formatted string

    Examples:
        # Example 1: Simple string message
        add_memory(messages="User likes watermelon", user_id="user123")

        # Example 2: Single message dict (MUST include 'role' field)
        add_memory(
            messages={"role": "user", "content": "I like watermelon"},
            user_id="user123"
        )

        # Example 3: Conversation message list (recommended format)
        add_memory(
            messages=[
                {"role": "user", "content": "Hello, my name is John"},
                {"role": "assistant", "content": "Hello John! Nice to meet you"},
                {"role": "user", "content": "I like watermelon and apples"}
            ],
            user_id="user123",
            agent_id="agent1"
        )

        # Example 4: With metadata
        add_memory(
            messages=[{"role": "user", "content": "My birthday is January 1st"}],
            user_id="user123",
            metadata={"source": "chat", "importance": "high"}
        )

    Note:
        - messages CANNOT be empty or blank
        - Each dict message MUST have 'role' (user/assistant/system) and 'content' fields
        - If 'role' is missing, it will be automatically set to 'user'
    """
    print(
        f"[add_memory] Called with user_id={user_id}, agent_id={agent_id}, run_id={run_id}, infer={infer}"
    )
    print(f"[add_memory] messages type: {type(messages).__name__}, content: {messages}")

    # Validate messages is not empty
    if not messages:
        print(f"[add_memory] Warning: Empty messages received: {messages}")
        return json.dumps(
            {
                "success": False,
                "error": "messages parameter cannot be empty. Please provide conversation content to store.",
            },
            ensure_ascii=False,
        )

    # If messages is a string, check it's not blank
    if isinstance(messages, str) and not messages.strip():
        print("[add_memory] Warning: Blank string messages received")
        return json.dumps(
            {
                "success": False,
                "error": "messages content cannot be blank. Please provide valid conversation content.",
            },
            ensure_ascii=False,
        )

    # If messages is a list, check if it has valid content and ensure proper format
    if isinstance(messages, list):
        valid_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content", "")
                if content and str(content).strip():
                    # Ensure 'role' field exists, default to 'user' if missing
                    if "role" not in msg:
                        msg = {**msg, "role": "user"}
                        print("[add_memory] Added default role 'user' to message")
                    valid_messages.append(msg)
            elif isinstance(msg, str) and msg.strip():
                # Convert string to proper message format
                valid_messages.append({"role": "user", "content": msg})
                print("[add_memory] Converted string message to dict format")

        if not valid_messages:
            print(f"[add_memory] Warning: List contains no valid messages: {messages}")
            return json.dumps(
                {
                    "success": False,
                    "error": "messages list contains no valid content. Each message must have non-empty content.",
                },
                ensure_ascii=False,
            )

        messages = valid_messages
        print(
            f"[add_memory] Valid messages count: {len(messages)}, formatted: {messages}"
        )

    try:
        memory = get_memory()
        result = memory.add(
            messages=messages,
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            metadata=metadata,
            infer=infer,
        )
        print("[add_memory] Successfully added memory")
        return format_memories_for_llm(result)
    except Exception as e:
        print(f"[add_memory] Error: {e}")
        return json.dumps(
            {"success": False, "error": f"Failed to add memory: {str(e)}"},
            ensure_ascii=False,
        )


@mcp.tool()
def search_memories(
    query: str,
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    limit: int = 10,
    threshold: Optional[float] = None,
    filters: Optional[Dict[str, Any]] = None,
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
        filters=filters,
    )
    print(f"[search_memories] result: {result}")
    return format_memories_for_llm(result)


@mcp.tool()
def get_memory_by_id(
    memory_id: int, user_id: Optional[str] = None, agent_id: Optional[str] = None
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
    metadata: Optional[Dict[str, Any]] = None,
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
        metadata=metadata,
    )
    return format_memories_for_llm(result)


@mcp.tool()
def delete_memory(
    memory_id: int, user_id: Optional[str] = None, agent_id: Optional[str] = None
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
    run_id: Optional[str] = None,
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
    filters: Optional[Dict[str, Any]] = None,
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
        user_id=user_id, agent_id=agent_id, run_id=run_id, limit=limit, offset=offset
    )
    return format_memories_for_llm(result)


# ============================================================================
# Part 3: User Profile Tools (6 tools for user profile management)
# ============================================================================


@mcp.tool()
def add_memory_with_profile(
    messages: Union[str, Dict, List[Dict]],
    user_id: str,
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    infer: bool = True,
    profile_type: str = "content",
    custom_topics: Optional[str] = None,
    strict_mode: bool = False,
) -> str:
    """
    Add memory and extract user profile information from conversation

    This tool performs two operations:
    1. Store the conversation messages as memories
    2. Extract user profile information using LLM and save it

    Args:
        messages: Conversation content, can be string, message dict, or message list.
            IMPORTANT: Each message dict MUST contain 'role' and 'content' fields.
        user_id: User identifier (required for profile extraction)
        agent_id: Agent identifier
        run_id: Run/session identifier
        metadata: Metadata dictionary
        infer: Whether to use intelligent mode (default True)
        profile_type: Type of profile extraction:
            - "content": Non-structured natural language profile (default)
            - "topics": Structured JSON topics with main topics and sub-topics
        custom_topics: Optional custom topics JSON string for structured extraction.
            Only used when profile_type="topics". Format:
            {"main_topic": {"sub_topic1": "description1", "sub_topic2": "description2"}}
        strict_mode: If True, only output topics from the provided list (default False)
            Only used when profile_type="topics"

    Returns:
        JSON formatted string containing:
        - Memory add results
        - profile_extracted: Whether profile was extracted
        - profile_content: Extracted profile text (when profile_type="content")
        - topics: Extracted structured topics (when profile_type="topics")

    Examples:
        # Example 1: Simple string message with user profile extraction
        add_memory_with_profile(
            messages="My name is John, I am 25 years old, and I like watermelon",
            user_id="user123"
        )

        # Example 2: Single message dict (MUST include 'role' field)
        add_memory_with_profile(
            messages={"role": "user", "content": "My hobbies are basketball and swimming"},
            user_id="user123"
        )

        # Example 3: Conversation message list (recommended format)
        add_memory_with_profile(
            messages=[
                {"role": "user", "content": "Hello, my name is John, I am 25 years old"},
                {"role": "assistant", "content": "Hello John! Nice to meet you, 25 is a vibrant age"},
                {"role": "user", "content": "Yes, I like playing basketball, I often exercise with friends on weekends"}
            ],
            user_id="user123",
            agent_id="agent1"
        )

        # Example 4: With structured topic extraction
        add_memory_with_profile(
            messages=[{"role": "user", "content": "I live in Beijing and work at a tech company"}],
            user_id="user123",
            profile_type="topics",
            custom_topics='{"personal_info": {"location": "residence", "occupation": "job title"}}'
        )

    Note:
        - messages CANNOT be empty or blank
        - user_id is REQUIRED for profile extraction
        - Each dict message MUST have 'role' (user/assistant/system) and 'content' fields
        - If 'role' is missing, it will be automatically set to 'user'
    """
    print(
        f"[add_memory_with_profile] Called with user_id={user_id}, agent_id={agent_id}, run_id={run_id}, infer={infer}, profile_type={profile_type}"
    )
    print(
        f"[add_memory_with_profile] messages type: {type(messages).__name__}, content: {messages}"
    )

    # Validate messages is not empty
    if not messages:
        print(f"[add_memory_with_profile] Warning: Empty messages received: {messages}")
        return json.dumps(
            {
                "success": False,
                "error": "messages parameter cannot be empty. Please provide conversation content to store.",
            },
            ensure_ascii=False,
        )

    # If messages is a string, check it's not blank
    if isinstance(messages, str) and not messages.strip():
        print("[add_memory_with_profile] Warning: Blank string messages received")
        return json.dumps(
            {
                "success": False,
                "error": "messages content cannot be blank. Please provide valid conversation content.",
            },
            ensure_ascii=False,
        )

    try:
        user_memory = get_user_memory()
        result = user_memory.add(
            messages=messages,
            user_id=user_id,
            agent_id=agent_id,
            run_id=run_id,
            metadata=metadata,
            infer=infer,
            profile_type=profile_type,
            custom_topics=custom_topics,
            strict_mode=strict_mode,
        )
        print(
            f"[add_memory_with_profile] Successfully added memory with profile for agent_id={agent_id}, user_id={user_id}, result={result}"
        )
        return format_memories_for_llm(result)
    except Exception as e:
        print(f"[add_memory_with_profile] Error: {e}")
        return json.dumps(
            {"success": False, "error": f"Failed to add memory with profile: {str(e)}"},
            ensure_ascii=False,
        )


@mcp.tool()
def search_memories_with_profile(
    query: str,
    user_id: str,
    agent_id: Optional[str] = None,
    run_id: Optional[str] = None,
    limit: int = 10,
    threshold: Optional[float] = None,
    filters: Optional[Dict[str, Any]] = None,
    add_profile: bool = True,
) -> str:
    """
    Search memories and optionally include user profile information

    This tool searches for relevant memories and can also return the user's profile
    to provide context about the user for personalized responses.

    Args:
        query: Search query text
        user_id: User identifier (required)
        agent_id: Agent identifier
        run_id: Run/session identifier
        limit: Maximum number of results (default 10)
        threshold: Similarity threshold (0.0-1.0)
        filters: Metadata filters
        add_profile: Whether to include user profile in results (default True)

    Returns:
        JSON formatted string containing:
        - Search results (memories)
        - profile_content: User's profile text (if add_profile=True and exists)
        - topics: User's structured topics (if add_profile=True and exists)
    """
    user_memory = get_user_memory()
    result = user_memory.search(
        query=query,
        user_id=user_id,
        agent_id=agent_id,
        run_id=run_id,
        limit=limit,
        threshold=threshold,
        filters=filters,
        add_profile=add_profile,
    )
    return format_memories_for_llm(result)


@mcp.tool()
def get_user_profile(user_id: str) -> str:
    """
    Get user profile information by user_id

    Retrieves the complete user profile including both non-structured content
    and structured topics if available.

    Args:
        user_id: User identifier (required)

    Returns:
        JSON formatted string containing:
        - id: Profile ID
        - user_id: User identifier
        - profile_content: Profile text description
        - topics: Structured topics dictionary
        - created_at: Creation timestamp
        - updated_at: Last update timestamp
        Or error message if not found
    """
    user_memory = get_user_memory()
    result = user_memory.profile(user_id=user_id)
    if result is None:
        return format_memories_for_llm(
            {"error": f"Profile for user {user_id} not found"}
        )
    return format_memories_for_llm(result)


@mcp.tool()
def list_user_profiles(
    user_id: Optional[str] = None,
    main_topic: Optional[List[str]] = None,
    sub_topic: Optional[List[str]] = None,
    topic_value: Optional[List[str]] = None,
    limit: int = 100,
    offset: int = 0,
) -> str:
    """
    List user profiles with optional filtering

    Retrieve multiple user profiles with filtering by topics. Useful for finding
    users with specific characteristics or interests.

    Args:
        user_id: Optional user identifier to filter by specific user
        main_topic: Optional list of main topic names to filter
            Example: ["basic_information", "interests_and_hobbies"]
        sub_topic: Optional list of sub topic paths in format "main_topic.sub_topic"
            Example: ["basic_information.user_name", "employment.company"]
        topic_value: Optional list of topic values to filter by exact match
            Example: ["Beijing", "Software Engineer"]
        limit: Maximum number of profiles to return (default 100)
        offset: Offset for pagination (default 0)

    Returns:
        JSON formatted string containing list of profile dictionaries
    """
    user_memory = get_user_memory()
    result = user_memory.profile_list(
        user_id=user_id,
        main_topic=main_topic,
        sub_topic=sub_topic,
        topic_value=topic_value,
        limit=limit,
        offset=offset,
    )
    return format_memories_for_llm({"profiles": result, "count": len(result)})


@mcp.tool()
def delete_user_profile(user_id: str) -> str:
    """
    Delete user profile by user_id

    Removes the user profile from storage. This does not delete the user's memories,
    only the extracted profile information.

    Args:
        user_id: User identifier (required)

    Returns:
        JSON formatted string with success status
    """
    user_memory = get_user_memory()
    success = user_memory.delete_profile(user_id=user_id)
    return format_memories_for_llm(
        {
            "success": success,
            "user_id": user_id,
            "message": f"Profile for user {user_id} deleted"
            if success
            else f"Profile for user {user_id} not found",
        }
    )


@mcp.tool()
def delete_memory_with_profile(
    memory_id: int,
    user_id: str,
    agent_id: Optional[str] = None,
    delete_profile: bool = False,
) -> str:
    """
    Delete memory and optionally the associated user profile

    Args:
        memory_id: Memory ID to delete
        user_id: User identifier (required)
        agent_id: Agent identifier
        delete_profile: If True, also delete the user's profile (default False)

    Returns:
        JSON formatted string with success status
    """
    user_memory = get_user_memory()
    success = user_memory.delete(
        memory_id=memory_id,
        user_id=user_id,
        agent_id=agent_id,
        delete_profile=delete_profile,
    )
    result = {
        "success": success,
        "memory_id": memory_id,
        "user_id": user_id,
    }
    if delete_profile:
        result["profile_deleted"] = delete_profile
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
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port number: {sys.argv[2]}, using default port 8000")
            port = 8000

    # Start server based on transport method
    if transport == "stdio":
        print("Starting PowerMem MCP Server with stdio transport...")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print(f"Starting PowerMem MCP Server with SSE transport on port {port}...")
        mcp.run(transport="sse", host="0.0.0.0", port=port, path=path)
    else:  # streamable-http
        print(
            f"Starting PowerMem MCP Server with streamable-http transport on port {port}..."
        )
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path=path)


if __name__ == "__main__":
    main()
