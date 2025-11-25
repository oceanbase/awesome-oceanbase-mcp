# OCP MCP Server

OceanBase Cloud Platform Model Context Protocol Server

## Installation

### Install from Source

#### 1. Clone the Repository

```bash
git clone https://github.com/oceanbase/awesome-oceanbase-mcp.git
cd awesome-oceanbase-mcp/src/ocp_mcp_server
```

#### 2. Install Python Package Manager and Create Virtual Environment

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # On Windows: `.venv\Scripts\activate`
```

#### 3. Configure Environment (Optional)

If you want to use a `.env` file for configuration:

```bash
cp .env.template .env
# Edit the .env file and fill in your OCP connection information
```

#### 4. Handle Network Issues (Optional)

If you encounter network issues, you can use Alibaba Cloud mirror:

```bash
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple/"
```

#### 5. Install Dependencies

```bash
uv pip install .
```

### Configuration

Configure OCP connection information in `.env`:

- `OCP_URL`: OCP server address
- `OCP_ACCESS_KEY_ID`: Access key ID
- `OCP_ACCESS_KEY_SECRET`: Access key secret

## 🚀 Quick Start

OCP MCP Server supports three transport modes:

### Stdio Mode

Add the following to your MCP client configuration file:

```json
{
  "mcpServers": {
    "ocp": {
      "command": "uv",
      "args": [
        "--directory", 
        "path/to/awesome-oceanbase-mcp/src/ocp_mcp_server",
        "run",
        "ocp_mcp_server"
      ],
      "env": {
        "OCP_URL": "localhost:8080",
        "OCP_ACCESS_KEY_ID": "your_ocp_access_key_id",
        "OCP_ACCESS_KEY_SECRET": "your_ocp_access_key_secret"
      }
    }
  }
}
```

### SSE Mode

Start the SSE mode server:

```bash
uv run ocp_mcp_server --transport sse --port 8000
```

**Parameters:**
- `--transport`: MCP server transport type (default: stdio)
- `--host`: Bind host (default: 127.0.0.1, use 0.0.0.0 to allow remote access)
- `--port`: Listen port (default: 8000)

**Alternative startup method (without uv):**
```bash
cd ocp_mcp/ && python3 -m server --transport sse --port 8000
```

**Configuration URL:** `http://ip:port/sse`

### Streamable HTTP Mode

Start the Streamable HTTP mode server:

```bash
uv run ocp_mcp_server --transport streamable-http --port 8000
```

**Alternative startup method (without uv):**
```bash
cd ocp_mcp/ && python3 -m server --transport streamable-http --port 8000
```

**Configuration URL:** `http://ip:port/mcp`

#### Client Configuration Examples

**VSCode Plugin Cline:**
```json
"streamable-ob": {
  "autoApprove": [],
  "disabled": false,
  "timeout": 60,
  "type": "streamableHttp",
  "url": "http://ip:port/mcp"
}
```

**Cursor:**
```json
"streamable-ob": {
  "autoApprove": [],
  "disabled": false,
  "timeout": 60,
  "type": "streamableHttp", // "type": "http" is also acceptable
  "url": "http://ip:port/mcp"
}
```

## Available Tools

### Cluster Management Tools

1. **`list_oceanbase_clusters`** - Query OceanBase cluster list
2. **`get_oceanbase_cluster_zones`** - Get cluster Zone list
3. **`get_oceanbase_cluster_servers`** - Get cluster OBServer list
4. **`get_oceanbase_zone_servers`** - Get OBServer list for specified Zone
5. **`get_oceanbase_cluster_stats`** - Get cluster resource statistics
6. **`get_oceanbase_cluster_server_stats`** - Get resource statistics for all OBServers in cluster
7. **`get_oceanbase_cluster_units`** - Query cluster Unit list
8. **`get_oceanbase_cluster_parameters`** - Get cluster parameter list
9. **`set_oceanbase_cluster_parameters`** - Update cluster parameters

### Tenant Management Tools

1. **`get_oceanbase_cluster_tenants`** - Query cluster tenant list
2. **`get_all_oceanbase_tenants`** - Query all tenant list
3. **`get_oceanbase_tenant_detail`** - Query tenant details
4. **`get_oceanbase_tenant_units`** - Query tenant Unit list
5. **`get_oceanbase_tenant_parameters`** - Get tenant parameter list
6. **`set_oceanbase_tenant_parameters`** - Update tenant parameters

### OBProxy Management Tools

1. **`list_obproxy_clusters`** - Query OBProxy cluster list
2. **`get_oceanbase_obproxy_cluster_detail`** - Query OBProxy cluster details
3. **`get_oceanbase_obproxy_cluster_parameters`** - Query OBProxy cluster parameters

### Database Object Management Tools

1. **`get_oceanbase_tenant_databases`** - Get tenant database list
2. **`get_oceanbase_tenant_users`** - Get tenant user list
3. **`get_oceanbase_tenant_user_detail`** - Get user details
4. **`get_oceanbase_tenant_roles`** - Get tenant role list
5. **`get_oceanbase_tenant_role_detail`** - Get role details
6. **`get_oceanbase_tenant_objects`** - Get tenant database object list

### Monitoring Tools

1. **`get_oceanbase_metric_groups`** - Query monitoring metric group information
2. **`get_oceanbase_metric_data_with_label`** - Query monitoring data with labels

### Alarm Tools

1. **`get_oceanbase_alarms`** - Query alarm event list
2. **`get_oceanbase_alarm_detail`** - Query alarm event details

### Inspection Tools

1. **`get_oceanbase_inspection_tasks`** - Query inspection task list
2. **`get_oceanbase_inspection_overview`** - Query inspection object list
3. **`get_oceanbase_inspection_report`** - Get inspection report details
4. **`run_oceanbase_inspection`** - Run inspection
5. **`get_oceanbase_inspection_item_last_result`** - Query last result of specified inspection item
6. **`get_oceanbase_inspection_report_info`** - Get last inspection result of specified object

### SQL Performance Analysis Tools

1. **`get_oceanbase_tenant_top_sql`** - Query SQL performance statistics
2. **`get_oceanbase_sql_text`** - Query SQL full text
3. **`get_oceanbase_tenant_slow_sql`** - Query slow SQL list

### Performance Report Tools

1. **`create_oceanbase_performance_report`** - Generate performance report
2. **`get_oceanbase_cluster_snapshots`** - Query cluster snapshot information
3. **`get_oceanbase_performance_report`** - Query performance report (returns HTML file)


## Community

When you need help, you can find developers and other community members at [https://github.com/oceanbase/awesome-oceanbase-mcp/](https://github.com/oceanbase/awesome-oceanbase-mcp/).

When you discover project issues, please create a new issue on the [issues](https://github.com/oceanbase/awesome-oceanbase-mcp) page.

## License

For more information, see [LICENSE](LICENSE).

