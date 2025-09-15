[English](README.md) | 简体中文<br>
# OceanBase MCP Server

OceanBase MCP Server 通过 MCP (模型上下文协议) 可以和 OceanBase 进行交互。
使用支持 MCP 的客户端，连接上 OB 数据库，可以列出所有的表、读取数据以及执行 SQL，然后可以使用大模型对数据库中的数据进一步分析。


## 特性

- 列出所有 OceanBase 数据库中的表作为资源
- 读取表中的数据
- 执行 SQL 语句
- AI 记忆系统
- 支持全文查询、向量查询和混合查询
- 鉴权
- 通过环境变量访问数据库
- 全面的日志记录

## 工具
- [✔️] 执行 SQL 语句
- [✔️] 查询当前租户
- [✔️] 查询所有的 server 节点信息 （仅支持 sys 租户）
- [✔️] 查询资源信息 （仅支持 sys 租户）
- [✔️] 查询 [ASH](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000002013776) 报告
- [✔️] 搜索 OceanBase 官网的文档（实验特性）  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;这个工具是实验性质的，因为相关 API 接口可能会变化。
- [✔️] 基于 OB Vector 的简单记忆系统（实验特性）
- [✔️] 使用全文查询在 OceanBase 中搜索文档
- [✔️] 在 OceanBase 中进行向量查询
- [✔️] 在 OceanBase 中进行向量和标量的混合查询

## 前提条件
你需要有一个 Oceanbase 数据库, 可以参考[安装文档](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000003378290)安装或者使用 [OceanBase Cloud](https://www.oceanbase.com/free-trial) 的免费试用。

## 源码安装

### 克隆仓库
```bash
git clone https://github.com/oceanbase/mcp-oceanbase.git
cd mcp-oceanbase/src/oceanbase_mcp_server
```
### 安装 Python 包管理器 uv 并创建虚拟环境
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate  # 在Windows系统上执行 `.venv\Scripts\activate`
```
### 如果使用 .env 文件配置 OceanBase 的连接信息，需要复制 .env.template 文件为 .env，然后修改 .env 文件
```bash
cp .env.template .env
```
### 如果因为网络问题 uv 下载文件较慢或者无法下载，可以使用阿里云的镜像源
```bash
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple/"
```
### 安装依赖
```bash
uv pip install .
```
## 从 PyPI 仓库安装
如果想通过 pip install 方式安装，请执行下面的命令。
```bash
uv pip install oceanbase-mcp
```
## 配置
有两种方式可以配置 OceanBase 的连接信息
1. 在环境变量中设置以下变量的值：
```bash
OB_HOST=localhost     # 数据库的地址
OB_PORT=2881         # 可选的数据库的端口（如果没有配置，默认是2881)
OB_USER=your_username
OB_PASSWORD=your_password
OB_DATABASE=your_database
```
2. 在 .env 文件中进行配置
## 使用方法

### Stdio 模式
在支持 MCP 的客户端中，将下面的内容填入配置文件，请根据实际信息修改
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
### SSE 模式
在 mcp-oceanbase/src/oceanbase_mcp_server 目录下，执行下面的命令，端口号是可配置的。  
'--transport'： MCP 的传输模式，默认是 stdio  
'--host'： 绑定的 host，默认是 127.0.0.1，也就是只能本机访问，如果需要远程访问，可以设置为 0.0.0.0  
'--port'： 监听的端口，默认是 8000
```bash
uv run oceanbase_mcp_server --transport sse --port 8000
```
如果不想使用 uv，也可以用下面的方式启动
```bash
cd oceanbase_mcp/ && python3 -m server --transport sse --port 8000
```
sse 模式访问地址示例： `http://ip:port/sse`

### Streamable HTTP 模式
在 mcp-oceanbase/src/oceanbase_mcp_server 目录下，执行下面的命令，端口号是可配置的。  
'--transport'： MCP 的传输模式，默认是 stdio  
'--host'：绑定的 host，默认是 127.0.0.1，也就是只能本机访问，如果需要远程访问，可以设置为 0.0.0.0  
'--port'：监听的端口，默认是 8000
```bash
uv run oceanbase_mcp_server --transport streamable-http --port 8000
```
如果不想使用 uv，也可以用下面的方式启动
```bash
cd oceanbase_mcp/ && python3 -m server --transport streamable-http --port 8000
```
Streamable HTTP 模式访问地址示例： `http://ip:port/mcp`

#### VsCode 插件 Cline 的示例配置
```json
"streamable-ob": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "type": "streamableHttp",
      "url": "http://ip:port/mcp"
    }
```
#### Cursor 的示例配置
```json
"streamable-ob": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "type": "streamableHttp", // “type”: “http” 也是可以的
      "url": "http://ip:port/mcp"
    }
```
#### CherryStudio 的示例配置
在 MCP->General->Type 的下拉框中选择 Streamable HTTP (streamableHttp)
### 鉴权
可以在环境变量或者 env 文件中配置 ALLOWED_TOKENS 变量，然后在 MCP Client 的请求头中增加“Authorization”: “Bearer \<token\>” 配置。只有携带有效 token 的请求可以访问 MCP 服务，如果有多个
token，可以使用英文的逗号分隔。  
示例配置：
```
ALLOWED_TOKENS=tokenOne,tokenTwo
``` 
#### CherryStudio
在 MCP->General->Headers 的输入框中增加 `Authorization=Bearer <token>` 的配置
#### Cursor
在 MCP 的配置文件里，像下面这样配置：
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
目前 Cline 在请求头增加的配置无法发送到 server 端。  
可以参考这个 [issue](https://github.com/cline/cline/issues/4391)。
### 🧠 AI 记忆系统

**实验特性**：基于 OceanBase 先进向量能力的持久化记忆系统，让您的 AI 助手拥有超强记忆力。

记忆系统使您的 AI 能够在对话间保持连续的上下文，无需重复告知个人偏好和信息。四个智能工具协同工作，创造无缝记忆体验：

- **`ob_memory_query`** - 语义搜索和检索相关记忆
- **`ob_memory_insert`** - 自动捕获和存储重要对话内容  
- **`ob_memory_delete`** - 删除过时或不需要的记忆
- **`ob_memory_update`** - 根据新信息演进和更新记忆

#### 🚀 快速设置

记忆工具**默认未启用**，以避免初始嵌入模型下载（0.1~4 GiB）耗时过久。使用以下环境变量启用智能记忆：

```bash
ENABLE_MEMORY=1 # 默认 0 表示关闭，设为 1 启用
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5 # 默认使用 BAAI/bge-small-en-v1.5 模型，如需更好体验可以更换为 BAAI/bge-m3 等其他模型
EMBEDDING_MODEL_PROVIDER=huggingface
```

#### 📋 前置条件

**向量支持**：需要 OceanBase v4.3.5.3+（默认启用向量特性）

```bash
sudo docker run -p 2881:2881 --name obvector -e MODE=mini -d oceanbase/oceanbase-ce:4.3.5.3-103000092025080818
```

**旧版本支持**：对于较旧的 OceanBase 版本，需要手动配置 [ob_vector_memory_limit_percentage](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000003381620) 开启向量能力。

#### ⬇️ 依赖安装
首先激活虚拟环境。  
如果使用的是源码安装，使用下面的命令来安装依赖
```bash
cd path/to/mcp-oceanbase/src/oceanbase_mcp_server
uv pip install -r pyproject.toml --extra memory
```
如果是 pip 的安装方式
```bash
uv pip install oceanbase-mcp[memory] --extra-index-url https://download.pytorch.org/whl/cpu
```
#### 💡 使用示例

体验跨会话智能记忆的强大能力：

```
📅 星期一对话
用户: "我喜欢足球和篮球，但是不喜欢游泳。另外我在上海工作，使用Python开发。"
AI: "好的，我已经记住了您的偏好和工作信息！" 
    💾 [自动调用 ob_memory_insert 保存偏好信息]

📅 星期三对话  
用户: "推荐一些我可能感兴趣的运动"
AI: 🔍 [自动调用 ob_memory_query 搜索"运动 偏好"]
    "根据您之前提到的偏好，我推荐足球和篮球相关的活动！您之前说过不太喜欢游泳，
     所以我为您推荐一些陆地运动..."

📅 一周后对话
用户: "我的工作地点在哪里？用什么编程语言？"  
AI: 🔍 [自动调用 ob_memory_query 搜索"工作 编程"]
    "您在上海工作，主要使用Python进行开发。"
```

**🎯 记忆系统优势**：
- ✅ **跨会话连续性** - 无需重复介绍自己
- ✅ **智能语义搜索** - 理解相关概念和上下文  
- ✅ **个性化体验** - AI真正"了解"您的喜好
- ✅ **自动化保存** - 重要信息无需手动记录

## 示例
下面是一些例子，展示了 OceanBase MCP Server 的一些功能。
### 例子 1: 列出所有的表
问题：
```plaintext
How many tables are there in the test database, and what are they?
```
回答：
```plaintext
Tables in test: 
t1
t2
```
### Example 2: 查看当前租户
问题：
```
What is my current tenant name?
```
回答：
```
Your current tenant name is 'sys'.
```
### 例子 3: 查看所有的 server 节点
你需要时 sys 租户才能查询所有 server 节点  
问题：
```
Query all server nodes
```
回答：
```
Successfully queried all server nodes. Here are the details:

| SVR_IP   | SVR_PORT | ID | ZONE  | SQL_PORT | WITH_ROOTSERVER | STATUS | START_SERVICE_TIME        | STOP_TIME | BLOCK_MIGRATE_IN_TIME | CREATE_TIME            | MODIFY_TIME            | BUILD_VERSION                                                                 | LAST_OFFLINE_TIME |
|----------|----------|----|-------|----------|-----------------|--------|---------------------------|-----------|-----------------------|-------------------------|-------------------------|------------------------------------------------------------------------------|-------------------|
| 127.0.0.1 | 2882     | 1  | zone1 | 2881     | YES             | ACTIVE | 2024-06-27 15:40:19.003123 | None      | None                  | 2024-06-19 16:39:11.749421 | 2024-06-27 15:40:21.001573 | 4.2.3.1_101000012024061216-c436ab3557c826ab31931d11ec836dc4df09d9de(Jun 12 2024 16:25:30) | None              |

This table provides comprehensive information about each server node, including IP addresses, ports, zones, statuses, and timestamps.
```
### 例子 4: 查看资源容量
你需要是 sys 租户，才可以查询资源容量  
问题：
```
Query the current resource capacity information
```
回答：
```
The current resource capacity information has been successfully queried. Here are the details:

| SVR_IP   | SVR_PORT | ZONE  | SQL_PORT | CPU_CAPACITY | CPU_CAPACITY_MAX | CPU_ASSIGNED | CPU_ASSIGNED_MAX | MEM_CAPACITY | MEM_ASSIGNED | LOG_DISK_CAPACITY | LOG_DISK_ASSIGNED | LOG_DISK_IN_USE | DATA_DISK_CAPACITY | DATA_DISK_IN_USE | DATA_DISK_HEALTH_STATUS | MEMORY_LIMIT | DATA_DISK_ALLOCATED | DATA_DISK_ABNORMAL_TIME | SSL_CERT_EXPIRED_TIME |
|----------|----------|-------|----------|--------------|------------------|--------------|------------------|--------------|--------------|-------------------|-------------------|-----------------|--------------------|-----------------|-------------------------|--------------|---------------------|-------------------------|-----------------------|
| 127.0.0.1 | 2882     | zone1 | 2881     | 4            | 4.0              | 2.0          | 2.0              | 5368709120    | 3221225472    | 5368709120         | 4294967296         | 3556769792       | 10737418240        | 664797184        | NORMAL                  | 6442450944    | 10737418240         | None                    | None                  |

This table provides comprehensive information about the resource capacities and assignments for the server.
```
### 例子 5: 拿到 ASH 报告
拿到 OceanBase Active Session History 报告  
问题：
```
Please provide me with today's ASH report.
```
回答：
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
### 例子 6: 使用全文查询检索文档
问题：
```
Find content in t2 table that mention "apple"
```
回答：
```
I have successfully queried the documents in the content field of table t2 that mention "apple". Here are the results:

1. Document ID: 2, Author: john, Age: 20, Content: I have a pear and an apple
2. Document ID: 1, Author: david, Age: 19, Content: I have a pineapple and an apple
3. Document ID: 3, Author: tom, Age: 21, Content: I also have a pear and an apple
```
### 例子 7: 向量查询
问题：
```
Please search for records in table t2 that are close to the vector [0.1, 0.1, 0.1].
```
回答：
```
The vector search on table t2 has returned results successfully. I can now analyze and present these results to the user.

The search found three records that are close to the vector [0.1, 0.1, 0.1]:

1. Record with id 2, name 'john', age 20, description 'I have a pear and an apple', vector '[0.1,0.1,0.2]', and distance 0.1
2. Record with id 3, name 'tom', age 21, description 'I also have a pear and an apple', vector '[0.1,0.1,0.2]', and distance 0.1
3. Record with id 1, name 'david', age 19, description 'I have a pineapple and an apple', vector '[0.1,0.2,0.3]', and distance 0.2236

These records are ordered by their distance from the search vector, with closer matches appearing first.
```
### 例子 8: 混合查询
进行关系条件过滤（即标量）和向量的混合查询，同时使用向量和标量作为查询条件  
问题：
```
Please find the record in table t2 that has a vector close to [0.1, 0.1, 0.2] and an age of 20.
```
回答：
```
The record in table `t2` that has a vector close to `[0.1, 0.1, 0.2]` and an age of 20 is:
(2, 'john', 20, 'I have a pear and an apple', '[0.1,0.1,0.2]', 0.0)
```

## 安全注意事项
- 不要提交环境变量信息或者凭证
- 使用最小权限的数据库用户
- 对于生产环境，考虑设置查询白名单
- 监控并记录所有的数据库操作

## 安全最佳实践
MCP 中的工具会访问数据库，为了安全：
1. **创建一个专用的 OceanBase 用户**，拥有最小的权限
2. **不要使用 root 用户**
3. **限制数据库的操作**，只运行必要的操作
4. **开启日志记录**，以便进行审计
5. **进行数据库访问的日常巡检**

## 许可证

Apache License - 查看 LICENSE 文件获取细节。

## 贡献

1. Fork 这个仓库
2. 创建你自己的分支 （`git checkout -b feature/amazing-feature`）
3. 提交修改 （`git commit -m 'Add some amazing feature'`）
4. 推送到远程仓库 （`git push origin feature/amazing-feature`）
5. 提交 PR