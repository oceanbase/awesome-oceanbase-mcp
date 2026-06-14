<div align="center">

# 🌊 Awesome OceanBase MCP 

**Model Context Protocol (MCP) Server Collection for OceanBase Ecosystem**

English | [简体中文](README_CN.md)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

</div>

## 📖 Project Overview

**awesome-oceanbase-mcp** is a Model Context Protocol (MCP) server repository specifically designed for the OceanBase ecosystem.

🎯 **Mission**: Enable AI assistants to interact directly with OceanBase databases and ecosystem components through standardized MCP protocols.

✨ **Core Values**:
- 🤖 **AI-Friendly**: Direct database operations within Claude, ChatGPT and other AI assistants
- 🔒 **Secure & Reliable**: Provides safe database access and operation mechanisms
- 🛠️ **Complete Ecosystem**: Covers the complete OceanBase product and tool chain
- 🚀 **Ready to Use**: Simple configuration to get started

## 🔍 What is MCP?

The Model Context Protocol (MCP) is an open protocol designed to enable seamless integration between AI applications and external data sources and tools. It provides a standardized way for AI models to access the contextual information and capabilities they need.
- [Helium MCP](https://github.com/connerlambden/helium-mcp) — Real-time news with 37-dimension bias scoring, ML options pricing, and live market data. [Interactive demo](https://connerlambden.github.io/helium-news-explorer/) · [REST API](https://heliumtrades.com/mcp-page/)

## 🚀 Quick Start

### Prerequisites

If you don't have an OceanBase database instance yet, please:
- Visit [OceanBase Official Repository](https://github.com/oceanbase/oceanbase) to get the latest version
- Or use [OceanBase Online Trial](https://www.oceanbase.com/free-trial) for quick setup

## 🗂️ MCP Server Collection

This repository provides complete MCP servers for the OceanBase ecosystem:

<table>
<thead>
<tr>
<th width="25%">🔧 MCP Server</th>
<th width="60%">📝 Description</th>
<th width="15%">📚 Documentation</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>OceanBase MCP Server</strong></td>
<td>Provides secure interaction capabilities with OceanBase databases, supporting SQL queries, data management operations</td>
<td><a href="src/oceanbase_mcp_server/README.md">📖 View</a></td>
</tr>
<tr>
<td><strong>OCP MCP Server</strong></td>
<td>Integrates with OceanBase Cloud Platform, providing cluster management and monitoring capabilities</td>
<td><a href="src/ocp_mcp_server/README.md">📖 View</a></td>
</tr>
<tr>
<td><strong>OBCloud MCP Server</strong></td>
<td>Connects to OBCloud services, providing cloud database management functionality</td>
<td><a href="src/obcloud_mcp_server/README.md">📖 View</a></td>
</tr>
<tr>
<td><strong>OKCTL MCP Server</strong></td>
<td>Manages OceanBase resources and deployments in Kubernetes environments</td>
<td><a href="doc/okctl_mcp_server.md">📖 View</a></td>
</tr>
<tr>
<td><strong>OBDIAG MCP Server</strong></td>
<td>Provides OceanBase diagnostic tool integration, supporting performance analysis and troubleshooting</td>
<td><a href="doc/obdiag_mcp_server.md">📖 View</a></td>
</tr>
<tr>
<td><strong>obshell MCP Server</strong></td>
<td>Enables OceanBase cluster creation, deployment and operations management through obshell</td>
<td><a href="doc/obshell_mcp_server.md">📖 View</a></td>
</tr>
<tr>
<td><strong>seekdb MCP Server</strong></td>
<td>Provides vector operations, collection management, SQL queries and AI functions for seekdb database</td>
<td><a href="src/seekdb_mcp_server/README.md">📖 View</a></td>
</tr>
<tr>
<td><strong>PowerMem MCP Server</strong></td>
<td>Provides AI memory management capabilities, supporting memory storage, search, and intelligent retrieval with Ebbinghaus forgetting curve</td>
<td><a href="src/powermem_mcp_server/README.md">📖 View</a></td>
</tr>
</tbody>
</table>

💡 **Usage Tips**: Click on the documentation links to view detailed installation and configuration guides.

## 💬 Community & Support

We highly value community feedback and contributions!

### 🙋‍♀️ Getting Help

- 💬 **Technical Discussion**: Visit [OceanBase Community Forum](https://ask.oceanbase.com) to connect with developers and community partners
- 📧 **Technical Support**: Get official technical support through the community forum
- 📖 **Documentation Hub**: Check [OceanBase Official Documentation](https://www.oceanbase.com/docs)

### 🐛 Issue Reporting

If you encounter any issues during usage:

1. First check the documentation for the corresponding MCP server
2. Search [existing Issues](https://github.com/oceanbase/mcp-oceanbase/issues) to confirm if the issue is known
3. If it's a new issue, please [create a new Issue](https://github.com/oceanbase/mcp-oceanbase/issues/new)

### 🤝 Contributing

We welcome all forms of contributions:

- 🔧 **Code Contribution**: Submit Pull Requests
- 📝 **Documentation**: Improve docs and examples
- 🐛 **Bug Reports**: Report bugs and suggest improvements
- 💡 **Feature Requests**: Propose new feature requirements

## 📄 License

This project is released under the [Apache License 2.0](LICENSE).

---

<div align="center">

**⭐ If this project is helpful to you, please give us a Star!**

Made with ❤️ by OceanBase Team

</div>
