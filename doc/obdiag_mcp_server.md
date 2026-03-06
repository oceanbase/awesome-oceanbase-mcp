# obdiag MCP Server

obdiag (OceanBase Diagnostic Tool) MCP Server.

English | [简体中文](obdiag_mcp_server_CN.md)

## Prerequisites

Before using the obdiag MCP Server, please ensure:

1. **obdiag is installed**: The server requires obdiag to be installed and accessible via the `obdiag` command.
2. **Configuration file exists**: At least one obdiag configuration file should exist in `~/.obdiag/` (e.g. `config.yml`).

For obdiag installation, please refer to:

[obdiag Download Link](https://www.oceanbase.com/softwarecenter)

[obdiag Installation Documentation](https://www.oceanbase.com/docs/common-obdiag-cn-1000000003892386)

## Startup
### Support for multiple types of MCP

You can start obdiag MCP with different protocols using the following commands:

```shell
uvx obdiag-mcp sse # sse mode, default port 8000 (recommended)
uvx obdiag-mcp stdio # stdio mode
uvx obdiag-mcp sse 8001 # sse mode, specify port 8001
uvx obdiag-mcp streamable-http # streamable-http mode, default port 8000
uvx obdiag-mcp streamable-http 8001 # streamable-http mode, specify port 8001
```

## Usage

Use with MCP Client, must use a client that supports Prompts, such as: Claude Desktop. Before entering a request, you need to manually select the required Prompt, then enter the request.

Claude Desktop config example:

```json
{
  "mcpServers": {
    "obdiag": {
      "url": "http://{host}:8000/mcp"
    }
  }
}
```

## Multi-Cluster Support

When you have multiple OceanBase clusters, place each cluster's config as a separate `.yml` file in `~/.obdiag/` (e.g. `ob_test.yml`, `ob_prod.yml`). Use the `cluster_name` parameter (file prefix without `.yml`) to specify which cluster to operate on.

- Call **obdiag_cluster_list** first to get available cluster names
- Pass `cluster_name` (e.g. `ob_test`) to other tools when needed
- If `cluster_name` is omitted, the default `config.yml` is used

## Available Tools

The obdiag MCP Server provides the following diagnostic tools:

- **obdiag_cluster_list**: List available cluster config names (file prefixes in `~/.obdiag/`, excluding `ai.yml`)
- **obdiag_check_run**: Execute cluster inspection and return inspection report
- **obdiag_analyze_log**: Analyze cluster logs to find error messages that have occurred
- **obdiag_display_list**: Query available diagnostic commands and return supported command list
- **obdiag_display_run**: Execute specific diagnostic commands with optional environment variables
- **obdiag_gather_log**: Collect cluster logs with optional filters (time range, grep, scope, etc.)

All tools except `obdiag_cluster_list` accept an optional `cluster_name` parameter to target a specific cluster.

## Community

When you need help, you can find developers and other community partners at [https://ask.oceanbase.com](https://ask.oceanbase.com).

When you discover project defects, please create a new issue on the [issues](https://github.com/oceanbase/mcp-oceanbase/issues) page.

## License

For more information, see [LICENSE](../LICENSE).