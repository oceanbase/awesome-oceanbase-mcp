# mcp-oceanbase

OBDiag (OceanBase Diagnostic Tool) MCP Server.

[English](obdiag_mcp_server.md) | 简体中文

## 使用方式

配合 MCP Client 使用，必须使用支持 Prompt 的客户端，如：Claude Desktop。输入请求前需要手动选取所需的 Prompt，然后输入请求。

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

## 支持多种类型的mcp
可通过如下指令启动不同协议的 obdiag mcp

```shell
cd src/obdiag_mcp_server
python server.py stdio # stdio 模式
python server.py sse # sse 模式，默认端口 8000
python server.py sse 8001 # sse 模式，指定端口 8001
python server.py streamable-http # streamable-http 模式，默认端口 8000
python server.py streamable-http 8001 # streamable-http 模式，指定端口 8001
```


## 前置条件

在使用 OBDiag MCP Server 之前，请确保：

1. **已安装 OBDiag**：服务器需要 OBDiag 已安装并可通过 `obdiag` 命令访问。
2. **配置文件存在**：OBDiag 配置文件应存在于 `~/.obdiag/config.yml`。

## 可用工具

OBDiag MCP Server 提供以下诊断工具：

- **obdiag_check_run**：执行集群巡检并返回巡检报告
- **obdiag_analyze_log**：分析集群日志，找出发生过的错误信息
- **obdiag_display_list**：查询可用的诊断命令并返回支持的指令列表
- **obdiag_display_run**：执行特定的诊断命令，支持可选的环境变量

## 社区

当你需要帮助时，你可以在 [https://ask.oceanbase.com](https://ask.oceanbase.com) 上找到开发者和其他的社区伙伴。

当你发现项目缺陷时，请在 [issues](https://github.com/oceanbase/mcp-oceanbase/issues) 页面创建一个新的 issue。

## 许可证

更多信息见 [LICENSE](../LICENSE)。
