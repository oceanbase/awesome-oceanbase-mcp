English | [简体中文](README_CN.md)<br>
# OceanBase MCP Server

A Model Context Protocol (MCP) server that enables secure interaction with OceanBase databases. 
This server allows AI assistants to list tables, read data, and execute SQL queries through a controlled interface, making database exploration and analysis safer and more structured.

## Features

- List available OceanBase tables as resources
- Read table contents
- Execute SQL queries with proper error handling
- AI Memory System
- Full text search, vector search and hybrid search
- Authorization
- Secure database access through environment variables
- Comprehensive logging

## Tools
- [✔️] Execute SQL queries
- [✔️] Get current tenant
- [✔️] Get all server nodes (sys tenant only)
- [✔️] Get resource capacity (sys tenant only)
- [✔️] Get [ASH](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000002013776) report
- [✔️] Search OceanBase document from official website(experimental)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This tool is experimental because the API on the official website may change.
- [✔️] Simple memory based on OB Vector(experimental)
- [✔️] Search for documents using full text search in an OceanBase table
- [✔️] Perform vector similarity search on an OceanBase table
- [✔️] Perform hybird search combining relational condition filtering(that is, scalar) and vector search
## Prerequisites
You need to have an Oceanbase database, you can refer to [this documentation](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000003378290) to install or use [OceanBase Cloud](https://www.oceanbase.com/free-trial) for free trial.

## Install from source code

### Clone the repository
```bash
git clone https://github.com/oceanbase/mcp-oceanbase.git
cd mcp-oceanbase/src/oceanbase_mcp_server
```
### Install the Python package manager uv and create virtual environment
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
```
### If you configure the OceanBase connection information using .env file. You should copy .env.template to .env and modify .env
```bash
cp .env.template .env
```
### If the dependency packages cannot be downloaded via uv due to network issues, you can change the mirror source to the Alibaba Cloud mirror source.
```bash
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple/"
```
### Install dependencies
```bash
uv pip install .
```
## Install from PyPI Repository
If you wish to use it via pip install, please execute the following command.
```bash
uv pip install oceanbase-mcp
```
## Configuration
There are two ways to configure the connection information of OceanBase
1. Set the following environment variables:

```bash
OB_HOST=localhost     # Database host
OB_PORT=2881         # Optional: Database port (defaults to 2881 if not specified)
OB_USER=your_username
OB_PASSWORD=your_password
OB_DATABASE=your_database
```
2. Configure in the .env file
## Usage

### Stdio Mode

Add the following content to the configuration file that supports the MCP server client:

```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "uv",
      "args": [
        "--directory", 
        "path/to/mcp-oceanbase/src/oceanbase_mcp_server",
        "run",
        "oceanbase_mcp_server"
      ],
      "env": {
        "OB_HOST": "localhost",
        "OB_PORT": "2881",
        "OB_USER": "your_username",
        "OB_PASSWORD": "your_password",
        "OB_DATABASE": "your_database"
      }
    }
  }
}
```
### SSE Mode
Within the mcp-oceanbase directory, execute the following command, the port can be customized as desired.  
'--transport': MCP server transport type, default is stdio  
'--host': host to bind to, default is 127.0.0.1, that is to say, you can only access it on your local computer. If you want any remote client to be able to access it, you can set the host to 0.0.0.0  
'--port': port to listen on, default is 8000
```bash
uv run oceanbase_mcp_server --transport sse --port 8000
```
If you don't want to use uv, you can start it in the following way
```bash
cd oceanbase_mcp/ && python3 -m server --transport sse --port 8000
```
The URL address for the general SSE mode configuration is `http://ip:port/sse`

### Streamable HTTP
Within the mcp-oceanbase directory, execute the following command, the port can be customized as desired.  
'--transport': MCP server transport type, default is stdio  
'--host': host to bind to, default is 127.0.0.1, that is to say, you can only access it on your local computer. If you want any remote client to be able to access it, you can set the host to 0.0.0.0  
'--port': port to listen on, default is 8000
```bash
uv run oceanbase_mcp_server --transport streamable-http --port 8000
```
If you don't want to use uv, you can start it in the following way
```bash
cd oceanbase_mcp/ && python3 -m server --transport streamable-http --port 8000
```
The URL address for the general Streamable HTTP mode configuration is `http://ip:port/mcp`

#### VSCode Extension Cline Sample Configuration
```json
"streamable-ob": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "type": "streamableHttp",
      "url": "http://ip:port/mcp"
    }
```
#### Cursor Sample Configuration
```json
"streamable-ob": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "type": "streamableHttp", // “type”: “http” is also acceptable
      "url": "http://ip:port/mcp"
    }
```
#### Cherry Studio Sample Configuration
MCP->General->Type, select Streamable HTTP (streamableHttp) from the dropdown menu.

### Authorization
The ALLOWED_TOKENS variable can be configured in environment variables or an env file. Then, add “Authorization”: “Bearer \<token\>” to the request header of the MCP Client. Only requests carrying a valid token can access the MCP server service. Multiple tokens can be separated by commas.  
For Example:
```
ALLOWED_TOKENS=tokenOne,tokenTwo
``` 
#### CherryStudio 
Add `Authorization=Bearer <token>` to the MCP->General->Headers input field.
#### Cursor
In the MCP configuration file, configure it as follows:
```json
{
  "mcpServers": {
    "ob-sse": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "type": "sse",
      "url": "http://ip:port/sse",
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```
#### Cline
Cline does not support setting Authorization in request headers.  
You can refer to this [issue](https://github.com/cline/cline/issues/4391).

### 🧠 AI Memory System

**Experimental Feature**: Transform your AI assistant with persistent vector-based memory powered by OceanBase's advanced vector capabilities.

The memory system enables your AI to maintain continuous context across conversations, eliminating the need to repeat personal preferences and information. Four intelligent tools work together to create a seamless memory experience:

- **`ob_memory_query`** - Semantically search and retrieve contextual memories
- **`ob_memory_insert`** - Automatically capture and store important conversations  
- **`ob_memory_delete`** - Remove outdated or unwanted memories
- **`ob_memory_update`** - Evolve memories with new information over time

#### 🚀 Quick Setup

Memory tools are **disabled by default** to avoid the initial embedding model download (0.5~4 GiB). Enable intelligent memory with these environment variables:

```bash
ENABLE_MEMORY=1  # default 0 disabled， set 1 to enable
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5 # default BAAI/bge-small-en-v1.5, You can set BAAI/bge-m3 or other models to get better experience.
EMBEDDING_MODEL_PROVIDER=huggingface
```

#### 📋 Prerequisites

**Vector Support**: Requires OceanBase v4.3.5.3+ (vector features enabled by default)

```bash
sudo docker run -p 2881:2881 --name obvector -e MODE=mini -d oceanbase/oceanbase-ce:4.3.5.3-103000092025080818
```

**Legacy Versions**: For older OceanBase versions, manually configure [ob_vector_memory_limit_percentage](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000003381620).

#### ⬇️ Dependency Installation
If you use source code Installation, use the following command to install dependencies
```bash
cd path/to/mcp-oceanbase/src/oceanbase_mcp_server
uv pip install -r pyproject.toml --extra memory
```
If pip Installation
```bash
uv pip install oceanbase-mcp[memory] --extra-index-url https://download.pytorch.org/whl/cpu
```

#### 💡 Usage Example

Experience the power of cross-session intelligent memory:

```
📅 Monday Conversation
User: "I love football and basketball, but I don't like swimming. I work in Shanghai using Python."
AI: "Got it! I've saved your preferences and work information!" 
    💾 [Automatically calls ob_memory_insert to save preference data]

📅 Wednesday Conversation  
User: "Recommend some sports I might be interested in"
AI: 🔍 [Automatically calls ob_memory_query searching "sports preferences"]
    "Based on your previous preferences, I recommend football and basketball activities! 
     Since you mentioned not liking swimming, here are some great land-based sports..."

📅 One Week Later
User: "Where do I work and what programming language do I use?"  
AI: 🔍 [Automatically calls ob_memory_query searching "work programming"]
    "You work in Shanghai and primarily use Python for development."
```

**🎯 Memory System Benefits**:
- ✅ **Cross-Session Continuity** - No need to reintroduce yourself
- ✅ **Intelligent Semantic Search** - Understands related concepts and context  
- ✅ **Personalized Experience** - AI truly "knows" your preferences
- ✅ **Automatic Capture** - Important information saved without manual effort
## Examples
Below are some examples demonstrating the capabilities of Oceanbase MCP Server.
### Example 1: Listing Tables
Question:
```plaintext
How many tables are there in the test database, and what are they?
```
Answer:
```plaintext
Tables in test: 
t1
t2
```
### Example 2: View the current tenant
Question:
```
What is my current tenant name?
```
Answer:
```
Your current tenant name is 'sys'.
```
### Example 3: View server nodes
You need to be sys tenant to get all server nodes.  
Question:
```
Query all server nodes
```
Answer:
```
Successfully queried all server nodes. Here are the details:

| SVR_IP   | SVR_PORT | ID | ZONE  | SQL_PORT | WITH_ROOTSERVER | STATUS | START_SERVICE_TIME        | STOP_TIME | BLOCK_MIGRATE_IN_TIME | CREATE_TIME            | MODIFY_TIME            | BUILD_VERSION                                                                 | LAST_OFFLINE_TIME |
|----------|----------|----|-------|----------|-----------------|--------|---------------------------|-----------|-----------------------|-------------------------|-------------------------|------------------------------------------------------------------------------|-------------------|
| 127.0.0.1 | 2882     | 1  | zone1 | 2881     | YES             | ACTIVE | 2024-06-27 15:40:19.003123 | None      | None                  | 2024-06-19 16:39:11.749421 | 2024-06-27 15:40:21.001573 | 4.2.3.1_101000012024061216-c436ab3557c826ab31931d11ec836dc4df09d9de(Jun 12 2024 16:25:30) | None              |

This table provides comprehensive information about each server node, including IP addresses, ports, zones, statuses, and timestamps.
```
### Example 4: View resource capacity
You need to be sys tenant to get resource capacity.  
Question:
```
Query the current resource capacity information
```
Answer:
```
The current resource capacity information has been successfully queried. Here are the details:

| SVR_IP   | SVR_PORT | ZONE  | SQL_PORT | CPU_CAPACITY | CPU_CAPACITY_MAX | CPU_ASSIGNED | CPU_ASSIGNED_MAX | MEM_CAPACITY | MEM_ASSIGNED | LOG_DISK_CAPACITY | LOG_DISK_ASSIGNED | LOG_DISK_IN_USE | DATA_DISK_CAPACITY | DATA_DISK_IN_USE | DATA_DISK_HEALTH_STATUS | MEMORY_LIMIT | DATA_DISK_ALLOCATED | DATA_DISK_ABNORMAL_TIME | SSL_CERT_EXPIRED_TIME |
|----------|----------|-------|----------|--------------|------------------|--------------|------------------|--------------|--------------|-------------------|-------------------|-----------------|--------------------|-----------------|-------------------------|--------------|---------------------|-------------------------|-----------------------|
| 127.0.0.1 | 2882     | zone1 | 2881     | 4            | 4.0              | 2.0          | 2.0              | 5368709120    | 3221225472    | 5368709120         | 4294967296         | 3556769792       | 10737418240        | 664797184        | NORMAL                  | 6442450944    | 10737418240         | None                    | None                  |

This table provides comprehensive information about the resource capacities and assignments for the server.
```
### Example 5: Get ASH report
Get OceanBase Active Session History report.  
Question:
```
Please provide me with today's ASH report.
```
Answer:
```
The ASH report for today (2025-09-03) has been successfully generated. Key findings include:

Cluster Overview:
- Name: ob6u2klmn4pwo0
- Observer Version: OceanBase 4.3.5.2
- OS: Linux(5.10.134-17.2.al8.x86_64)_x86_64
- Analysis period: 2025-09-03 00:00:00 to 2025-09-03 11:26:40
- Average Active Sessions: 0.45

Top Activity:
1. Tenant t6wxyssara4e8 dominated background activity (99.99%)
2. Nodes 10.102.32.82, 10.102.64.254, and 10.102.49.151 showed highest activity
3. Primary activities:
   - TenantWeakReadService generating cluster versions
   - LogService I/O operations
   - TimerWK background tasks
   - LSRecoveryService reporting

Resource Utilization:
- Main wait events: exec inner sql wait (various), palf write, sync rpc
- Top IO operations: COMPACTION tasks (TX_TABLE_MERGE, MINI_MERGE)
- Primary SQL activity: SELECT statements (17.36% of activity)

The complete report contains detailed breakdowns of:
- Node-specific activity
- IO bandwidth usage
- Latch waits
- Object access patterns
- Execution phases
- SQL execution statistics

Would you like me to extract or highlight any specific sections of the report?
```
### Example 6: Search for documents using full text search
Question:
```
Find content in t2 table that mention "apple"
```
Answer:
```
I have successfully queried the documents in the content field of table t2 that mention "apple". Here are the results:

1. Document ID: 2, Author: john, Age: 20, Content: I have a pear and an apple
2. Document ID: 1, Author: david, Age: 19, Content: I have a pineapple and an apple
3. Document ID: 3, Author: tom, Age: 21, Content: I also have a pear and an apple
```
### Example 7: Search records by vector similarity
Question:
```
Please search for records in table t2 that are close to the vector [0.1, 0.1, 0.1].
```
Answer:
```
The vector search on table t2 has returned results successfully. I can now analyze and present these results to the user.

The search found three records that are close to the vector [0.1, 0.1, 0.1]:

1. Record with id 2, name 'john', age 20, description 'I have a pear and an apple', vector '[0.1,0.1,0.2]', and distance 0.1
2. Record with id 3, name 'tom', age 21, description 'I also have a pear and an apple', vector '[0.1,0.1,0.2]', and distance 0.1
3. Record with id 1, name 'david', age 19, description 'I have a pineapple and an apple', vector '[0.1,0.2,0.3]', and distance 0.2236

These records are ordered by their distance from the search vector, with closer matches appearing first.
```
### Example 8: Perform hybird search
Perform hybird search combining relational condition filtering(that is, scalar) and vector search. 
Using both vectors and scalars as query conditions.  
Question:
```
Please find the record in table t2 that has a vector close to [0.1, 0.1, 0.2] and an age of 20.
```
Answer:
```
The record in table `t2` that has a vector close to `[0.1, 0.1, 0.2]` and an age of 20 is:
(2, 'john', 20, 'I have a pear and an apple', '[0.1,0.1,0.2]', 0.0)
```

## Security Considerations

- Never commit environment variables or credentials
- Use a database user with minimal required permissions
- Consider implementing query whitelisting for production use
- Monitor and log all database operations

## Security Best Practices

This MCP server requires database access to function. For security:

1. **Create a dedicated OceanBase user** with minimal permissions
2. **Never use root credentials** or administrative accounts
3. **Restrict database access** to only necessary operations
4. **Enable logging** for audit purposes
5. **Regular security reviews** of database access

See [OceanBase Security Configuration Guide](./SECURITY.md) for detailed instructions on:
- Creating a restricted OceanBase user
- Setting appropriate permissions
- Monitoring database access
- Security best practices

⚠️ IMPORTANT: Always follow the principle of least privilege when configuring database access.

## License

Apache License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

