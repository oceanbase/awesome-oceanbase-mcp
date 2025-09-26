<div align="center">

# 🌊 Awesome MCP OceanBase

**为 OceanBase 生态系统打造的 Model Context Protocol (MCP) 服务集合**

[English](README.md) | 简体中文

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

</div>

## 📖 项目简介

**awesome-mcp-oceanbase** 是一个专为 OceanBase 生态系统设计的 Model Context Protocol (MCP) 服务资源库。

🎯 **项目目标**：通过标准化的 MCP 协议，让 AI 助手能够直接与 OceanBase 数据库及其生态组件进行智能交互。

✨ **核心价值**：
- 🤖 **AI 友好**：在 Claude、ChatGPT 等 AI 助手中直接操作数据库
- 🔒 **安全可靠**：提供安全的数据库访问和操作机制
- 🛠️ **生态完整**：覆盖 OceanBase 完整的产品和工具链
- 🚀 **开箱即用**：简单配置即可开始使用

## 🔍 什么是 MCP？

Model Context Protocol (MCP) 是一个开放协议，旨在实现 AI 应用程序与外部数据源和工具之间的无缝集成。它为 AI 模型提供了一种标准化的方式来访问所需的上下文信息和工具能力。

## 🚀 快速开始

### 前置条件

如果您还没有 OceanBase 数据库实例，请先：
- 访问 [OceanBase 官方仓库](https://github.com/oceanbase/oceanbase) 获取最新版本
- 或使用 [OceanBase 在线体验](https://www.oceanbase.com/free-trial) 快速启动

## 🗂️ MCP 服务列表

本仓库提供了完整的 OceanBase 生态 MCP 服务：

<table>
<thead>
<tr>
<th width="25%">🔧 MCP 服务</th>
<th width="60%">📝 功能描述</th>
<th width="15%">📚 文档</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>OceanBase MCP Server</strong></td>
<td>提供与 OceanBase 数据库的安全交互能力，支持 SQL 查询、数据管理等操作</td>
<td><a href="src/oceanbase_mcp_server/README_CN.md">📖 查看</a></td>
</tr>
<tr>
<td><strong>OCP MCP Server</strong></td>
<td>与 OceanBase Cloud Platform 集成，提供集群管理和监控能力</td>
<td><a href="doc/ocp_mcp_server_CN.md">📖 查看</a></td>
</tr>
<tr>
<td><strong>OBCloud MCP Server</strong></td>
<td>连接 OBCloud 云服务，提供云端数据库管理功能</td>
<td><a href="src/obcloud_mcp_server/README.md">📖 查看</a></td>
</tr>
<tr>
<td><strong>OKCTL MCP Server</strong></td>
<td>管理 Kubernetes 环境中的 OceanBase 资源和部署</td>
<td><a href="doc/okctl_mcp_server_CN.md">📖 查看</a></td>
</tr>
<tr>
<td><strong>OBDIAG MCP Server</strong></td>
<td>提供 OceanBase 诊断工具集成，支持性能分析和故障排查</td>
<td><a href="doc/obdiag_mcp_server_CN.md">📖 查看</a></td>
</tr>
<tr>
<td><strong>obshell MCP Server</strong></td>
<td>通过 obshell 实现 OceanBase 集群的创建、部署和运维管理</td>
<td><a href="doc/obshell_mcp_server_CN.md">📖 查看</a></td>
</tr>
</tbody>
</table>

💡 **使用提示**：点击对应的文档链接查看详细的安装和配置指南。

## 💬 社区与支持

我们非常重视社区的反馈和贡献！

### 🙋‍♀️ 获取帮助

- 💬 **技术讨论**：访问 [OceanBase 社区论坛](https://ask.oceanbase.com) 与开发者和社区伙伴交流
- 📧 **技术支持**：通过社区论坛获得官方技术支持
- 📖 **文档中心**：查看 [OceanBase 官方文档](https://www.oceanbase.com/docs)

### 🐛 问题反馈

如果您在使用过程中遇到任何问题：

1. 首先查看对应 MCP 服务的文档
2. 搜索 [现有 Issues](https://github.com/oceanbase/mcp-oceanbase/issues) 确认问题是否已知
3. 如果是新问题，请 [创建新 Issue](https://github.com/oceanbase/mcp-oceanbase/issues/new) 

### 🤝 贡献指南

欢迎所有形式的贡献：

- 🔧 **代码贡献**：提交 Pull Request
- 📝 **文档改进**：完善文档和示例
- 🐛 **问题报告**：报告 Bug 和建议改进
- 💡 **功能建议**：提出新功能需求

## 📄 许可协议

本项目基于 [Apache License 2.0](LICENSE) 开源协议发布。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！**

Made with ❤️ by OceanBase Team

</div>
