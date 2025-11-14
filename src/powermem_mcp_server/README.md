# PowerMem MCP Server

PowerMem MCP Server - Model Context Protocol server for PowerMem memory management.

English | [简体中文](powermem_mcp_server_CN.md)

## Prerequisites

Before using the PowerMem MCP Server, please ensure:

1. **PowerMem is installed**: The server requires PowerMem to be installed. You can install it via:
   ```shell
   pip install powermem
   ```

2. **Configuration file exists**: Create a `.env` file in your working directory or project root with PowerMem configuration. The server will automatically search for `.env` files in:
   - Current working directory's `.env`
   - Project root directory's `.env`
   - `examples/configs/.env`

For PowerMem installation and configuration, please refer to:

[PowerMem Documentation](https://powermem.ai/docs)

## Startup

### Support for multiple types of MCP

You can start PowerMem MCP with different protocols using the following commands:

```shell
uvx powermem-mcp sse # sse mode, default port 8000 (recommended)
uvx powermem-mcp stdio # stdio mode
uvx powermem-mcp sse 8001 # sse mode, specify port 8001
uvx powermem-mcp streamable-http # streamable-http mode, default port 8000
uvx powermem-mcp streamable-http 8001 # streamable-http mode, specify port 8001
```

## Usage

Use with MCP Client, must use a client that supports Prompts, such as: Claude Desktop. Before entering a request, you need to manually select the required Prompt, then enter the request.

Claude Desktop config example:

```json
{
  "mcpServers": {
    "powermem": {
      "url": "http://{host}:8000/mcp"
    }
  }
}
```

## Available Tools

The PowerMem MCP Server provides the following memory management tools:

- **add_memory**: Add new memory to storage. Supports string, message dict, or message list format. Can use intelligent mode for automatic inference.
- **search_memories**: Search memories by query text with optional filters, limit, and similarity threshold.
- **get_memory_by_id**: Get a specific memory by its ID.
- **update_memory**: Update the content and metadata of an existing memory.
- **delete_memory**: Delete a specific memory by its ID.
- **delete_all_memories**: Batch delete memories by user_id, agent_id, or run_id.
- **list_memories**: List all memories with pagination support (limit and offset) and optional filters.

## Community

When you need help, you can find developers and other community partners at [https://github.com/oceanbase/powermem](https://github.com/oceanbase/powermem).

When you discover project defects, please create a new issue on the [issues](https://github.com/oceanbase/powermem/issues) page.

## License

For more information, see [LICENSE](LICENSE).
