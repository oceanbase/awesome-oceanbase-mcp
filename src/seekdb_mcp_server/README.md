English | [简体中文](README_CN.md)

# seekdb mcp server

A Model Context Protocol (MCP) server that enables interaction with seekdb database. This server allows AI assistants to perform vector operations, manage collections, execute SQL queries and leverage AI functions through a controlled interface, making database exploration and analysis safer and more structured.

## 📋 Table of Contents

- [Features](#-features)
- [Available Tools](#%EF%B8%8F-available-tools)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Install seekdb](#install-seekdb)
  - [Install seekdb mcp server](#install-seekdb-mcp-server)
- [Configuration](#%EF%B8%8F-configuration)
- [Quickstart](#-quickstart)
- [Advanced Features](#-advanced-features)
  - [AI Memory System](#-ai-memory-system)
- [Examples](#-examples)
- [Security](#-security)
- [License](#-license)
- [Contributing](#-contributing)

## ✨ Features

- **Vector Collection Management**: Create, list, query, and manage vector collections
- **Advanced Search**: Full-text search, vector similarity search, and hybrid search
- **AI Functions**: Integrate with AI models for embedding, completion, and reranking
- **AI Memory System**: Persistent vector-based memory for AI assistants
- **Data Import/Export**: Import CSV files to seekdb and export data to CSV
- **SQL Operations**: Execute SQL queries on seekdb

## 🛠️ Available Tools

### Vector Collection Tools

| Tool | Description |
|------|-------------|
| `create_collection` | Create a new vector collection with configurable dimension and distance metric |
| `list_collections` | List all collections in seekdb |
| `has_collection` | Check if a collection exists |
| `peek_collection` | Preview documents in a collection |
| `add_data_to_collection` | Add documents with auto-generated embeddings |
| `update_collection` | Update existing documents in a collection |
| `delete_documents` | Delete documents by ID or filter conditions |
| `query_collection` | Query documents using vector similarity search |
| `delete_collection` | Delete a collection and all its data |

### Search Tools

| Tool | Description |
|------|-------------|
| `full_text_search` | Perform full-text search using MATCH...AGAINST syntax |
| `hybrid_search` | Combine full-text search and vector search with RRF ranking |

### AI Model Tools

| Tool | Description |
|------|-------------|
| `create_ai_model` | Register an AI model (embedding, completion, or rerank) |
| `create_ai_model_endpoint` | Create an endpoint connecting a model to an API service |
| `drop_ai_model` | Remove a registered AI model |
| `drop_ai_model_endpoint` | Remove an AI model endpoint |
| `ai_complete` | Call an LLM for text generation |
| `ai_rerank` | Rerank documents by relevance using an AI model |
| `get_registered_ai_models` | List all registered AI models |
| `get_ai_model_endpoints` | List all AI model endpoints |

### Memory Tools

| Tool | Description |
|------|-------------|
| `seekdb_memory_query` | Semantic search for stored memories |
| `seekdb_memory_insert` | Store new memories with metadata |
| `seekdb_memory_delete` | Delete memories by ID |
| `seekdb_memory_update` | Update existing memories |

### Data Import/Export Tools

| Tool | Description |
|------|-------------|
| `import_csv_file_to_seekdb` | Import CSV data as a table or vector collection |
| `export_csv_file_from_seekdb` | Export table or collection data to CSV |

### Database Tools

| Tool | Description |
|------|-------------|
| `execute_sql` | Execute SQL queries on seekdb |
| `get_current_time` | Get current time from seekdb database |


## 📋 Prerequisites

### seekdb Requirements

seekdb supports two deployment modes:

- **Embedded Mode**: seekdb runs as a library inside your application
  - Supported OS: Linux (glibc >= 2.28)
  - Supported Python: 3.11 to 3.13 (pyseekdb), CPython 3.8 to 3.14 (pylibseekdb)
  - Supported Architecture: x86_64, aarch64

- **Client/Server Mode**: Connect to a deployed seekdb
## 🚀 Installation

### Install seekdb

seekdb can be installed as an embedded library. Use pip to install:

```bash
# Install pyseekdb (recommended, includes embedded seekdb)
pip install pyseekdb

# Or use a mirror for faster installation
pip install pyseekdb -i https://pypi.tuna.tsinghua.edu.cn/simple
```

If prompted that the pip version is too low, upgrade pip first:

```bash
pip install --upgrade pip
```

### Install seekdb mcp server

Install from PyPI:

```bash
pip install seekdb-mcp-server
```

Or install from source:

```bash
git clone https://github.com/oceanbase/awesome-oceanbase-mcp.git
cd awesome-oceanbase-mcp/src/seekdb_mcp_server
pip install .
```

## ⚙️ Configuration

seekdb mcp server uses embedded seekdb by default, which requires no additional configuration. The server automatically initializes the database when started.

## 🚀 Quickstart

seekdb mcp server supports **stdio** transport mode only.

### Stdio Mode

Add the following content to your MCP client configuration file:

**Using uvx (recommended):**

```json
{
  "mcpServers": {
    "seekdb": {
      "command": "uvx",
      "args": [
        "seekdb-mcp-server"
      ]
    }
  }
}
```

**Running from source:**

```json
{
  "mcpServers": {
    "seekdb": {
      "command": "uv",
      "args": [
        "--directory",
        "path/to/awesome-oceanbase-mcp/src/seekdb_mcp_server",
        "run",
        "seekdb-mcp-server"
      ]
    }
  }
}
```

## 🔧 Advanced Features

### 🧠 AI Memory System

The AI Memory System enables your AI assistant to maintain persistent vector-based memory powered by seekdb's vector capabilities.

The memory system allows your AI to maintain continuous context across conversations, eliminating the need to repeat personal preferences and information. Four intelligent tools work together to create a seamless memory experience:

- **`seekdb_memory_query`** - Semantically search and retrieve contextual memories
- **`seekdb_memory_insert`** - Automatically capture and store important conversations
- **`seekdb_memory_delete`** - Remove outdated or unwanted memories
- **`seekdb_memory_update`** - Evolve memories with new information over time

#### Memory System Features

- ✅ **Cross-Session Continuity** - No need to reintroduce yourself
- ✅ **Intelligent Semantic Search** - Understands related concepts and context
- ✅ **Personalized Experience** - AI truly "knows" your preferences
- ✅ **Automatic Capture** - Important information saved without manual effort
- ✅ **Multilingual Support** - Store and query memories in any language

#### Memory Categories

The memory system intelligently organizes information by category:

- **Sports/Fitness**: football, basketball, swimming, gym, yoga, running, etc.
- **Food/Drinks**: coffee, tea, pizza, sushi, vegan preferences, etc.
- **Work/Career**: job, position, company, skills, projects, etc.
- **Personal**: birthday, hometown, family, languages, hobbies, etc.
- **Technology**: programming languages, frameworks, databases, tools, etc.
- **Entertainment**: movies, music, books, games, genres, etc.

## 📚 Examples

### Collection Operations

**User:** Create a Collection named "document"

**AI:** I've successfully created a collection named **"document"** in seekdb with the following default settings:
- **Dimension**: 384 (vector size)
- **Distance metric**: L2 (Euclidean distance)

---

**User:** Insert two sentences into the document: Machine learning is a subset of artificial intelligence, and vector databases enable semantic search

**AI:** Done! I've inserted two sentences into the **"document"** collection:

| ID | Document |
|------|----------|
| doc1 | Machine learning is a subset of artificial intelligence |
| doc2 | vector databases enable semantic search |

---

**User:** Query documents related to machine learning

**AI:** Here are the documents related to **"machine learning"**, ranked by relevance:

| Rank | ID | Document | Distance |
|------|------|----------|----------|
| 1 | doc1 | Machine learning is a subset of artificial intelligence | 5.44 |
| 2 | doc2 | vector databases enable semantic search | 7.83 |

---

**User:** Update the document about machine learning to "Python is a popular programming language."

**AI:** Done! I've updated the document:

| ID | Before | After |
|------|--------|-------|
| doc1 | Machine learning is a subset of artificial intelligence | Python is a popular programming language. |

---

**User:** Delete the document about vector database

**AI:** Done! I've deleted the document about vector databases:

| ID | Deleted Document |
|------|------------------|
| doc2 | vector databases enable semantic search |

---

**User:** Query all documents in the document

**AI:** Here are all the documents in the **"document"** collection:

| ID | Document | Metadata |
|------|----------|----------|
| doc1 | Python is a popular programming language. | {} |

The collection currently contains **1 document**.

---

**User:** Delete the collection document

**AI:** Done! The collection **"document"** has been permanently deleted along with all its data.

### Search Tools

**User:** Create a collection, hybrid_search_test

**AI:** Done! The collection `hybrid_search_test` has been created successfully with:
- **Dimension**: 384
- **Distance metric**: L2

---

**User:** Insert the following documents:
- "The weather forecast predicts sunny skies for the weekend."
- "Mount Everest is the highest mountain peak in the world."
- "Ocean waves crash against the rocky shoreline at sunset."
- "Apple is a delicious red fruit that grows on trees in orchards."
- "The new iPhone 17 Pro features an advanced camera system and titanium design."

**AI:** Done! Successfully added 5 documents to the `hybrid_search_test` collection:

| ID | Document |
|------|----------|
| doc1 | The weather forecast predicts sunny skies for the weekend. |
| doc2 | Mount Everest is the highest mountain peak in the world. |
| doc3 | Ocean waves crash against the rocky shoreline at sunset. |
| doc4 | Apple is a delicious red fruit that grows on trees in orchards. |
| doc5 | The new iPhone 17 Pro features an advanced camera system and titanium design. |

---

**User:** Perform a hybrid_search, full-text keyword "apple", semantic search "apple smartphone technology"

**AI:** Here are the hybrid search results combining full-text keyword **"apple"** and semantic query **"apple smartphone technology"**:

| Rank | ID | Document |
|------|------|----------|
| 1 | doc4 | Apple is a delicious red fruit that grows on trees in orchards. |
| 2 | doc5 | The new iPhone 17 Pro features an advanced camera system and titanium design. |
| 3 | doc2 | Mount Everest is the highest mountain peak in the world. |
| 4 | doc1 | The weather forecast predicts sunny skies for the weekend. |
| 5 | doc3 | Ocean waves crash against the rocky shoreline at sunset. |

**Analysis:**
- **doc4** ranks first due to the strong full-text match with the literal word "Apple"
- **doc5** ranks second because it matches semantically with "smartphone technology" (iPhone is an Apple smartphone), even though it doesn't contain the word "apple" explicitly
- The remaining documents have lower relevance scores as they don't match either search criterion well

The hybrid search successfully combined keyword matching (BM25) with semantic similarity (vector search) using Reciprocal Rank Fusion (RRF) to produce these ranked results.

---

## 🔒 Security

This MCP server uses embedded seekdb by default, which runs locally within your application.

### Security Best Practices

1. **Local Data Storage**: Embedded seekdb stores data locally, ensuring data privacy
2. **No Network Exposure**: stdio mode doesn't expose any network endpoints
3. **File Permissions**: Ensure proper file permissions for the data directory

### Security Checklist

- ✅ Data stays local with embedded mode
- ✅ No credentials required for embedded mode
- ✅ No network ports exposed
- ✅ Standard file system security applies

## 📄 License

Apache License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create your feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**
