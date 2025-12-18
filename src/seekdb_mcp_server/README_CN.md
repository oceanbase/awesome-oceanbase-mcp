[English](README.md) | 简体中文

# seekdb MCP Server

一个模型上下文协议 (MCP) 服务器，用于与 seekdb 数据库进行交互。该服务器允许 AI 助手通过受控接口执行向量操作、管理集合、执行 SQL 查询以及利用 AI 函数，使数据库探索和分析更加安全和结构化。

## 📋 目录

- [特性](#-特性)
- [可用工具](#%EF%B8%8F-可用工具)
- [前提条件](#-前提条件)
- [安装](#-安装)
  - [安装 seekdb](#安装-seekdb)
  - [安装 seekdb mcp server](#安装-seekdb-mcp-server)
- [配置](#%EF%B8%8F-配置)
- [快速开始](#-快速开始)
- [高级功能](#-高级功能)
  - [AI 记忆系统](#-ai-记忆系统)
- [示例](#-示例)
- [安全](#-安全)
- [许可证](#-许可证)
- [贡献](#-贡献)

## ✨ 特性

- **向量集合管理**: 创建、列出、查询和管理向量集合
- **高级搜索**: 全文搜索、向量相似性搜索和混合搜索
- **AI 函数**: 集成 AI 模型进行嵌入、文本生成和重排序
- **AI 记忆系统**: 为 AI 助手提供基于向量的持久化记忆
- **数据导入/导出**: 导入 CSV 文件到 seekdb 并将数据导出为 CSV
- **SQL 操作**: 在 seekdb 上执行 SQL 查询

## 🛠️ 可用工具

### 向量集合工具

| 工具 | 描述 |
|------|------|
| `create_collection` | 创建具有可配置维度和距离度量的新向量集合 |
| `list_collections` | 列出 seekdb 中的所有集合 |
| `has_collection` | 检查集合是否存在 |
| `peek_collection` | 预览集合中的文档 |
| `add_data_to_collection` | 添加具有自动生成嵌入的文档 |
| `update_collection` | 更新集合中的现有文档 |
| `delete_documents` | 按 ID 或过滤条件删除文档 |
| `query_collection` | 使用向量相似性搜索查询文档 |
| `delete_collection` | 删除集合及其所有数据 |

### 搜索工具

| 工具 | 描述 |
|------|------|
| `full_text_search` | 使用 MATCH...AGAINST 语法执行全文搜索 |
| `hybrid_search` | 结合全文搜索和向量搜索，使用 RRF 排序 |

### AI 模型工具

| 工具 | 描述 |
|------|------|
| `create_ai_model` | 注册 AI 模型（嵌入、文本生成或重排序） |
| `create_ai_model_endpoint` | 创建将模型连接到 API 服务的端点 |
| `drop_ai_model` | 移除已注册的 AI 模型 |
| `drop_ai_model_endpoint` | 移除 AI 模型端点 |
| `ai_complete` | 调用 LLM 进行文本生成 |
| `ai_rerank` | 使用 AI 模型按相关性重排文档 |
| `get_registered_ai_models` | 列出所有已注册的 AI 模型 |
| `get_ai_model_endpoints` | 列出所有 AI 模型端点 |

### 记忆工具

| 工具 | 描述 |
|------|------|
| `seekdb_memory_query` | 对存储的记忆进行语义搜索 |
| `seekdb_memory_insert` | 存储带有元数据的新记忆 |
| `seekdb_memory_delete` | 按 ID 删除记忆 |
| `seekdb_memory_update` | 更新现有记忆 |

### 数据导入/导出工具

| 工具 | 描述 |
|------|------|
| `import_csv_file_to_seekdb` | 将 CSV 数据导入为表或向量集合 |
| `export_csv_file_from_seekdb` | 将表或集合数据导出为 CSV |

### 数据库工具

| 工具 | 描述 |
|------|------|
| `execute_sql` | 在 seekdb 上执行 SQL 查询 |
| `get_current_time` | 从 seekdb 数据库获取当前时间 |


## 📋 前提条件

### seekdb 要求

seekdb 支持两种部署模式：

- **嵌入式模式**: seekdb 作为库运行在你的应用程序内
  - 支持的操作系统: Linux (glibc >= 2.28)
  - 支持的 Python 版本: 3.11 到 3.13 (pyseekdb), CPython 3.8 到 3.14 (pylibseekdb)
  - 支持的架构: x86_64, aarch64

- **客户端/服务器模式**: 连接到已部署的 seekdb

## 🚀 安装

### 安装 seekdb

seekdb 可以作为嵌入式库安装。使用 pip 安装：

```bash
# 安装 pyseekdb（推荐，包含嵌入式 seekdb）
pip install pyseekdb

# 或使用镜像加速安装
pip install pyseekdb -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果提示 pip 版本过低，请先升级 pip：

```bash
pip install --upgrade pip
```

### 安装 seekdb mcp server

从 PyPI 安装：

```bash
pip install seekdb-mcp-server
```

或从源码安装：

```bash
git clone https://github.com/oceanbase/awesome-oceanbase-mcp.git
cd awesome-oceanbase-mcp/src/seekdb_mcp_server
pip install .
```

## ⚙️ 配置

seekdb mcp server 默认使用嵌入式 seekdb，无需额外配置。服务器启动时会自动初始化数据库。

## 🚀 快速开始

seekdb mcp server 仅支持 **stdio** 传输模式。

### Stdio 模式

在你的 MCP 客户端配置文件中添加以下内容：

**使用 uvx（推荐）：**

```json
{
  "mcpServers": {
    "seekdb": {
      "command": "uvx",
      "args": [
        "seekdb_mcp_server"
      ]
    }
  }
}
```

**从源码运行：**

```json
{
  "mcpServers": {
    "seekdb": {
      "command": "uv",
      "args": [
        "--directory",
        "path/to/awesome-oceanbase-mcp/src/seekdb_mcp_server",
        "run",
        "seekdb_mcp_server"
      ]
    }
  }
}
```

## 🔧 高级功能

### 🧠 AI 记忆系统

AI 记忆系统使你的 AI 助手能够基于 seekdb 的向量能力维护持久化的向量记忆。

记忆系统使你的 AI 能够在对话间保持连续的上下文，无需重复告知个人偏好和信息。四个智能工具协同工作，创造无缝记忆体验：

- **`seekdb_memory_query`** - 语义搜索和检索相关记忆
- **`seekdb_memory_insert`** - 自动捕获和存储重要对话内容
- **`seekdb_memory_delete`** - 删除过时或不需要的记忆
- **`seekdb_memory_update`** - 根据新信息演进和更新记忆

#### 记忆系统特性

- ✅ **跨会话连续性** - 无需重复介绍自己
- ✅ **智能语义搜索** - 理解相关概念和上下文
- ✅ **个性化体验** - AI 真正"了解"你的偏好
- ✅ **自动捕获** - 重要信息无需手动保存
- ✅ **多语言支持** - 以任何语言存储和查询记忆

#### 记忆分类

记忆系统按类别智能组织信息：

- **运动/健身**: 足球、篮球、游泳、健身房、瑜伽、跑步等
- **食物/饮品**: 咖啡、茶、披萨、寿司、素食偏好等
- **工作/职业**: 职位、公司、技能、项目等
- **个人信息**: 生日、家乡、家庭、语言、爱好等
- **技术**: 编程语言、框架、数据库、工具等
- **娱乐**: 电影、音乐、书籍、游戏、类型等

## 📚 示例

### 集合操作

**用户:** 创建一个名为 "document" 的集合

**AI:** 我已成功在 seekdb 中创建了名为 **"document"** 的集合，使用以下默认设置：
- **维度**: 384（向量大小）
- **距离度量**: L2（欧几里得距离）

---

**用户:** 向 document 中插入两句话：机器学习是人工智能的一个子集，向量数据库支持语义搜索

**AI:** 完成！我已将两句话插入到 **"document"** 集合中：

| ID | 文档 |
|------|----------|
| doc1 | 机器学习是人工智能的一个子集 |
| doc2 | 向量数据库支持语义搜索 |

---

**用户:** 查询与机器学习相关的文档

**AI:** 以下是与 **"机器学习"** 相关的文档，按相关性排序：

| 排名 | ID | 文档 | 距离 |
|------|------|----------|----------|
| 1 | doc1 | 机器学习是人工智能的一个子集 | 5.44 |
| 2 | doc2 | 向量数据库支持语义搜索 | 7.83 |

---

**用户:** 将关于机器学习的文档更新为 "Python 是一种流行的编程语言。"

**AI:** 完成！我已更新该文档：

| ID | 更新前 | 更新后 |
|------|--------|-------|
| doc1 | 机器学习是人工智能的一个子集 | Python 是一种流行的编程语言。 |

---

**用户:** 删除关于向量数据库的文档

**AI:** 完成！我已删除关于向量数据库的文档：

| ID | 已删除的文档 |
|------|------------------|
| doc2 | 向量数据库支持语义搜索 |

---

**用户:** 查询 document 中的所有文档

**AI:** 以下是 **"document"** 集合中的所有文档：

| ID | 文档 | 元数据 |
|------|----------|----------|
| doc1 | Python 是一种流行的编程语言。 | {} |

该集合当前包含 **1 个文档**。

---

**用户:** 删除 document 集合

**AI:** 完成！集合 **"document"** 及其所有数据已被永久删除。

### 搜索工具

**用户:** 创建一个集合 hybrid_search_test

**AI:** 完成！集合 `hybrid_search_test` 已成功创建：
- **维度**: 384
- **距离度量**: L2

---

**用户:** 插入以下文档：
- "天气预报预测周末将是晴天。"
- "珠穆朗玛峰是世界上最高的山峰。"
- "日落时分海浪拍打着岩石海岸。"
- "苹果是一种美味的红色水果，生长在果园的树上。"
- "新款 iPhone 17 Pro 配备先进的相机系统和钛金属设计。"

**AI:** 完成！已成功向 `hybrid_search_test` 集合添加 5 个文档：

| ID | 文档 |
|------|----------|
| doc1 | 天气预报预测周末将是晴天。 |
| doc2 | 珠穆朗玛峰是世界上最高的山峰。 |
| doc3 | 日落时分海浪拍打着岩石海岸。 |
| doc4 | 苹果是一种美味的红色水果，生长在果园的树上。 |
| doc5 | 新款 iPhone 17 Pro 配备先进的相机系统和钛金属设计。 |

---

**用户:** 执行混合搜索，全文关键词 "apple"，语义搜索 "apple smartphone technology"

**AI:** 以下是结合全文关键词 **"apple"** 和语义查询 **"apple smartphone technology"** 的混合搜索结果：

| 排名 | ID | 文档 |
|------|------|----------|
| 1 | doc4 | 苹果是一种美味的红色水果，生长在果园的树上。 |
| 2 | doc5 | 新款 iPhone 17 Pro 配备先进的相机系统和钛金属设计。 |
| 3 | doc2 | 珠穆朗玛峰是世界上最高的山峰。 |
| 4 | doc1 | 天气预报预测周末将是晴天。 |
| 5 | doc3 | 日落时分海浪拍打着岩石海岸。 |

**分析:**
- **doc4** 排名第一，因为与字面词 "Apple" 有很强的全文匹配
- **doc5** 排名第二，因为它与 "smartphone technology"（智能手机技术）语义匹配（iPhone 是苹果的智能手机），尽管它没有明确包含 "apple" 这个词
- 其余文档相关性得分较低，因为它们与两种搜索条件都不太匹配

混合搜索成功地使用倒数排名融合 (RRF) 算法结合了关键词匹配 (BM25) 和语义相似性（向量搜索）来产生这些排序结果。

---

## 🔒 安全

此 MCP 服务器默认使用嵌入式 seekdb，在你的应用程序本地运行。

### 安全最佳实践

1. **本地数据存储**: 嵌入式 seekdb 在本地存储数据，确保数据隐私
2. **无网络暴露**: stdio 模式不暴露任何网络端点
3. **文件权限**: 确保数据目录有适当的文件权限

### 安全检查清单

- ✅ 嵌入式模式下数据保持本地
- ✅ 嵌入式模式无需凭证
- ✅ 无网络端口暴露
- ✅ 适用标准文件系统安全

## 📄 许可证

Apache License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

我们欢迎贡献！请按照以下步骤：

1. **Fork 仓库**
2. **创建你的功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **提交你的修改**
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **推送到分支**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **创建 Pull Request**
