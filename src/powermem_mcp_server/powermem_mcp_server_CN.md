# PowerMem MCP Server

PowerMem MCP Server - 用于 PowerMem 内存管理的模型上下文协议服务器。

[English](README.md) | 简体中文

## 前置条件

在使用 PowerMem MCP Server 之前，请确保：

1. **已安装 PowerMem**：服务器需要 PowerMem 已安装。您可以通过以下方式安装：
   ```shell
   pip install powermem
   ```

2. **配置文件存在**：在工作目录或项目根目录创建 `.env` 文件，包含 PowerMem 配置。服务器会自动在以下位置搜索 `.env` 文件：
   - 当前工作目录的 `.env`
   - 项目根目录的 `.env`
   - `examples/configs/.env`

   您可以复制 `.env.example` 文件作为模板：
   ```shell
   cp powermem_mcp/.env.example .env
   ```
   
   然后编辑 `.env` 文件并配置以下关键设置：
   
   - **数据库提供商**：从 `sqlite`、`oceanbase` 或 `postgres` 中选择
   - **LLM 提供商**：从 `qwen`、`openai` 或 `mock` 中选择
   - **嵌入模型提供商**：从 `qwen`、`openai` 或 `mock` 中选择
   - **API 密钥**：设置您的 LLM 和嵌入模型 API 密钥
   - **代理配置**：配置内存管理设置
   - **智能内存**：启用/配置艾宾浩斯遗忘曲线设置
   - **性能**：调整批次大小、缓存设置和搜索参数
   - **安全**：配置加密和访问控制
   - **日志**：设置日志级别和文件路径
   
   `.env.example` 文件包含详细的注释和不同用例的示例配置。

PowerMem 安装和配置请参考：

[PowerMem 文档](https://powermem.ai/docs)

## 启动

### 支持多种类型的 MCP

可通过如下指令启动不同协议的 PowerMem MCP：

```shell
uvx powermem-mcp sse # sse 模式，默认端口 8000（推荐使用）
uvx powermem-mcp stdio # stdio 模式
uvx powermem-mcp sse 8001 # sse 模式，指定端口 8001
uvx powermem-mcp streamable-http # streamable-http 模式，默认端口 8000
uvx powermem-mcp streamable-http 8001 # streamable-http 模式，指定端口 8001
```

## 使用方式

配合 MCP Client 使用，必须使用支持 Prompt 的客户端，如：Claude Desktop。输入请求前需要手动选取所需的 Prompt，然后输入请求。

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

## 可用工具

PowerMem MCP Server 提供以下内存管理工具：

- **add_memory**：向存储中添加新记忆。支持字符串、消息字典或消息列表格式。可使用智能模式进行自动推理。
- **search_memories**：通过查询文本搜索记忆，支持可选过滤器、限制和相似度阈值。
- **get_memory_by_id**：根据 ID 获取特定记忆。
- **update_memory**：更新现有记忆的内容和元数据。
- **delete_memory**：根据 ID 删除特定记忆。
- **delete_all_memories**：根据 user_id、agent_id 或 run_id 批量删除记忆。
- **list_memories**：列出所有记忆，支持分页（limit 和 offset）和可选过滤器。

## 社区

当你需要帮助时，你可以在 [https://github.com/oceanbase/powermem](https://github.com/oceanbase/powermem) 上找到开发者和其他的社区伙伴。

当你发现项目缺陷时，请在 [issues](https://github.com/oceanbase/powermem/issues) 页面创建一个新的 issue。

## 许可证

更多信息见 [LICENSE](LICENSE)。
