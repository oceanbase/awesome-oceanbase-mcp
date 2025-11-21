# OCP MCP Server

OceanBase Cloud Platform Model Context Protocol Server

## 功能特性

- 支持 OCP API 签名认证
- 提供多种传输方式：stdio、sse、streamable-http
- 实现 MCP 协议规范
- 支持 OCP 监控数据查询
- **OceanBase 集群管理**：查询集群列表、状态筛选、名称搜索等

## 可用工具

### 集群管理工具

1. **`list_oceanbase_clusters`** - 查询 OceanBase 集群列表
   - 支持分页查询（page, size）
   - 支持排序（sort）
   - 支持按集群名称搜索（name）
   - 支持按状态筛选（status）

2. **`get_cluster_info`** - 获取所有集群信息（简化版本）

3. **`get_running_clusters`** - 获取所有运行中的集群

4. **`search_clusters_by_name`** - 根据集群名称搜索集群

### 集群状态说明

- `RUNNING`: 运行中
- `CREATING`: 创建中  
- `DELETING`: 删除中
- `STARTING`: 启动中
- `RESTARTING`: 重启中
- `STOPPING`: 停止中
- `STOPPED`: 已停止
- `TAKINGOVER`: 接管中
- `MOVINGOUT`: 迁出中
- `SWITCHOVER`: 主备集群切换中
- `FAILOVER`: 备集群故障恢复中
- `OPERATING`: 运维中

## 安装

```bash
pip install -e .
```

## 使用方法

### 命令行启动

```bash
# stdio 模式（默认）
uv run ocp_mcp_server

# SSE 模式
uv run ocp_mcp_server --transport sse --host 127.0.0.1 --port 8000

# Streamable HTTP 模式
uv run ocp_mcp_server --transport streamable-http --host 127.0.0.1 --port 8000
```

### 配置

在使用前需要配置 OCP 连接信息：

- `OCP_URL`: OCP 服务器地址
- `OCP_ACCESS_KEY_ID`: 访问密钥 ID
- `OCP_ACCESS_KEY_SECRET`: 访问密钥


## 🚀 快速开始

OCP MCP Server 支持三种传输模式：

### Stdio 模式

在你的 MCP 客户端配置文件中添加以下内容：

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

### SSE 模式

启动 SSE 模式服务器：

```bash
uv run ocp_mcp_server --transport sse --port 8000
```

**参数说明:**
- `--transport`: MCP 服务器传输类型（默认: stdio）
- `--host`: 绑定的主机（默认: 127.0.0.1，使用 0.0.0.0 允许远程访问）
- `--port`: 监听端口（默认: 8000）

**替代启动方式（不使用 uv）:**
```bash
cd ocp_mcp/ && python3 -m server --transport sse --port 8000
```

**配置 URL:** `http://ip:port/sse`

### Streamable HTTP 模式

启动 Streamable HTTP 模式服务器：

```bash
uv run ocp_mcp_server --transport streamable-http --port 8000
```

**替代启动方式（不使用 uv）:**
```bash
cd ocp_mcp/ && python3 -m server --transport streamable-http --port 8000
```

**配置 URL:** `http://ip:port/mcp`

#### 客户端配置示例

**VSCode 插件 Cline:**
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
  "type": "streamableHttp", // "type": "http" 也是可以的
  "url": "http://ip:port/mcp"
}
```

## 使用示例

### 查询集群列表

```python
# 获取第一页的 10 个集群，按名称升序排列
result = list_oceanbase_clusters(
    page=1, 
    size=10, 
    sort="name,asc"
)

# 搜索名称包含 "test" 的集群
result = list_oceanbase_clusters(name="test")

# 查询运行中和创建中的集群
result = list_oceanbase_clusters(
    status=["RUNNING", "CREATING"],
    size=50
)
```

### 集群信息结构

返回的集群信息包含以下主要字段：

```json
{
  "data": {
    "contents": [
      {
        "id": 1000002,
        "name": "test-cluster",
        "obClusterId": 4,
        "obVersion": "2.2.73",
        "status": "RUNNING",
        "type": "PRIMARY",
        "regionCount": 1,
        "tenantCount": 5,
        "serverCount": 3,
        "rootServers": [...],
        "zones": [...],
        "createTime": "2020-11-29T22:23:12+08:00",
        "loadType": "EXPRESS_OLTP"
      }
    ],
    "page": {
      "number": 1,
      "size": 10,
      "totalElements": 25,
      "totalPages": 3
    }
  },
  "successful": true,
  "status": 200
}
```

## 测试

运行测试脚本验证工具功能：

```bash
python test_cluster_tools.py
```