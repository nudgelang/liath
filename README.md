# 🚀 Liath: Your AI-Powered Database System

> Liath is a next-generation database system that combines the power of key-value storage, vector search, and AI capabilities into one flexible platform. Built on RocksDB/LevelDB with Lua as its query language, it's designed for developers who want to build AI-powered applications quickly and efficiently.

## ✨ Key Features

Liath comes packed with powerful features to help you build AI-powered applications. Here's a quick overview:

- 🔌 **Pluggable Storage**: Choose between RocksDB and LevelDB
- 📝 **Lua Query Language**: Write powerful queries with familiar syntax
- 🧩 **Plugin Architecture**: Extend functionality with custom plugins
- 🔍 **Vector Search**: Built-in vector database capabilities
- 🤖 **AI Integration**: Direct access to language models
- 📊 **Embedding Generation**: Create and manage text embeddings
- 📁 **File Operations**: Built-in file storage and retrieval
- 🏷️ **Namespaces**: Isolate data and operations
- 💾 **Transaction Support**: ACID compliant (RocksDB)
- 🔐 **User Authentication**: Secure user management
- 🌐 **CLI & HTTP API**: Multiple ways to interact
- 💾 **Backup & Restore**: Keep your data safe
- ⚡ **Query Caching**: Optimize performance
- 📈 **Monitoring**: Track system performance
- 🔄 **Connection Pooling**: Handle high concurrency

> 📚 For detailed information about each feature, check out our [Features Documentation](FEATURES.md)

## 🛠️ Installation

1. **Prerequisites**
   - Python 3.11 or higher
   - Poetry package manager

2. **Install Poetry**
   ```bash
   pip install poetry
   ```

3. **Clone & Setup**
   ```bash
   git clone https://github.com/nudgelang/liath.git
   cd liath
   poetry install
   ```

4. **Create Directory Structure**
   ```bash
   mkdir -p data/default/{files,luarocks} plugins
   ```

5. **Install Lua Dependencies**
   ```bash
   ./liath/setup_luarocks.sh
   ```

## 🚀 Quick Start

### CLI Mode
```bash
poetry run cli --storage auto
```

### Server Mode
```bash
poetry run server --storage auto --host 0.0.0.0 --port 5000
```

### Basic Operations

```lua
-- Create user and login
create_user username password
login username password

-- Create and use namespace
create_namespace my_namespace
use my_namespace

-- Basic queries
query return db:put("key", "value")
query return db:get("key")
```

## 📦 Using LuaRocks Packages

Liath supports LuaRocks packages in your queries. Here's how:

1. **Install a Package**
   ```bash
   luarocks install --tree=./data/namespaces/your_namespace package_name
   ```

2. **Use in Queries**
   ```lua
   local json = db:require("cjson")
   return json.encode({key = "value"})
   ```

### Example: HTTP Requests with LuaSocket

```lua
local http = db:require("socket.http")
local body, code = http.request("http://example.com")
return {body = body, status_code = code}
```

## 🔄 Storage Options

Choose your storage backend based on your needs:

| Feature | RocksDB | LevelDB |
|---------|---------|---------|
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Transactions | ✅ | ❌ |
| Column Families | ✅ | ❌ |
| Complexity | Medium | Low |

## 🧩 Extending Liath

Create custom plugins by:
1. Adding a new Python file in `plugins/`
2. Inheriting from `PluginBase`
3. Implementing required methods

## 🤝 Contributing

We welcome contributions! Feel free to:
- Submit pull requests
- Report bugs
- Suggest features
- Improve documentation

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.
