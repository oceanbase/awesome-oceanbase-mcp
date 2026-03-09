# OCP MCP Server

OceanBase Cloud Platform Model Context Protocol Server

## 使用方法

### 从源码安装

#### 1. 克隆仓库

```bash
git clone https://github.com/oceanbase/awesome-oceanbase-mcp.git
cd awesome-oceanbase-mcp/src/ocp_mcp_server
```

#### 2. 安装 Python 包管理器并创建虚拟环境
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv venv
source .venv/bin/activate  # 在Windows系统上执行 `.venv\Scripts\activate`
```

#### 3. 配置环境（可选）
如果你想使用 `.env` 文件进行配置：
```bash
cp .env.template .env
# 编辑 .env 文件，填入你的 ocp 连接信息
```

#### 4. 处理网络问题（可选）
如果遇到网络问题，可以使用阿里云镜像：
```bash
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple/"
```

#### 5. 安装依赖
```bash
uv pip install .
```

### 配置

在.env配置 OCP 连接信息：

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

## 可用工具

### 集群管理

1. **`list_oceanbase_clusters`** - 查询 OceanBase 集群列表
2. **`get_oceanbase_cluster_zones`** - 获取集群 Zone 列表
3. **`get_oceanbase_cluster_servers`** - 获取集群 OBServer 列表
4. **`get_oceanbase_zone_servers`** - 获取指定 Zone 的 OBServer 列表
5. **`get_oceanbase_cluster_stats`** - 获取集群资源统计信息
6. **`get_oceanbase_cluster_server_stats`** - 获取集群所有 OBServer 的资源统计
7. **`get_oceanbase_cluster_units`** - 查询集群 Unit 列表
8. **`get_oceanbase_cluster_parameters`** - 获取集群参数列表
9. **`set_oceanbase_cluster_parameters`** - 更新集群参数

### 租户管理

1. **`get_oceanbase_cluster_tenants`** - 查询集群租户列表
2. **`get_all_oceanbase_tenants`** - 查询所有租户列表
3. **`get_oceanbase_tenant_detail`** - 查询租户详情
4. **`get_oceanbase_tenant_units`** - 查询租户 Unit 列表
5. **`get_oceanbase_tenant_parameters`** - 获取租户参数列表
6. **`set_oceanbase_tenant_parameters`** - 更新租户参数

### OBProxy 管理

1. **`list_obproxy_clusters`** - 查询 OBProxy 集群列表
2. **`get_oceanbase_obproxy_cluster_detail`** - 查询 OBProxy 集群详情
3. **`get_oceanbase_obproxy_cluster_parameters`** - 查询 OBProxy 集群参数

### 数据库对象管理

1. **`get_oceanbase_tenant_databases`** - 获取租户数据库列表
2. **`get_oceanbase_tenant_users`** - 获取租户用户列表
3. **`get_oceanbase_tenant_user_detail`** - 获取用户详情
4. **`get_oceanbase_tenant_roles`** - 获取租户角色列表
5. **`get_oceanbase_tenant_role_detail`** - 获取角色详情
6. **`get_oceanbase_tenant_objects`** - 获取租户数据库对象列表

### 监控告警

1. **`get_oceanbase_metric_groups`** - 查询监控指标组信息
2. **`get_oceanbase_metric_data_with_label`** - 查询带标签的监控数据
3. **`get_oceanbase_alarms`** - 查询告警事件列表
4. **`get_oceanbase_alarm_detail`** - 查询告警事件详情

### 巡检

1. **`get_oceanbase_inspection_tasks`** - 查询巡检任务列表
2. **`get_oceanbase_inspection_overview`** - 查询巡检对象列表
3. **`get_oceanbase_inspection_report`** - 获取巡检报告详情
4. **`run_oceanbase_inspection`** - 执行巡检
5. **`get_oceanbase_inspection_item_last_result`** - 查询指定巡检项的最后结
6. **`get_oceanbase_inspection_report_info`** - 获取指定对象的最后巡检结果

### SQL 性能分析

1. **`get_oceanbase_tenant_top_sql`** - 查询 SQL 性能统计
2. **`get_oceanbase_sql_text`** - 查询 SQL 完整文本
3. **`get_oceanbase_tenant_slow_sql`** - 查询慢 SQL 列表
 
### 性能报告

1. **`create_oceanbase_performance_report`** - 生成性能报告
2. **`get_oceanbase_cluster_snapshots`** - 查询集群快照信息
3. **`get_oceanbase_performance_report`** - 查询性能报告（返回 HTML 文件）


## 社区

当你需要帮助时，你可以在 [https://github.com/oceanbase/awesome-oceanbase-mcp](https://github.com/oceanbase/awesome-oceanbase-mcp) 上找到开发者和其他的社区伙伴。

当你发现项目缺陷时，请在 [issues](https://github.com/oceanbase/awesome-oceanbase-mcp/issues) 页面创建一个新的 issue。

## 许可证

更多信息见 [LICENSE](LICENSE)。