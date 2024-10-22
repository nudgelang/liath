# Liath

Liath is an advanced, extensible database system built on top of RocksDB or LevelDB with Lua as its query language. It combines the power of key-value storage, vector search, LLM capabilities, and file operations into a flexible and modular architecture.

## Features

- **Pluggable Storage Backend**: Choose between RocksDB and LevelDB
- **Lua Query Language**: Flexible and powerful querying capabilities
- **Plugin Architecture**: Easily extensible with custom plugins
- **Vector Database**: Built-in vector search capabilities
- **LLM Integration**: Direct access to language models for text generation and completion
- **Embedding Generation**: Create embeddings for text data
- **File Operations**: Built-in file storage and retrieval
- **Namespaces**: Isolate data and operations in separate namespaces
- **Transaction Support**: ACID compliant transactions (RocksDB only)
- **User Authentication**: Basic user management and authentication
- **CLI and Server Interfaces**: Interact via command line or HTTP API
- **Backup and Restore**: Create and manage backups of your data
- **Query Caching**: Improve performance for frequently executed queries
- **Monitoring and Logging**: Track system performance and log important events
- **Connection Pooling**: Efficiently handle high concurrency in the server

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/terraprompt/liath.git
   cd liath
   ```

2. Install the required Python dependencies:
   ```
   pip install flask pyyaml
   ```

3. Install the storage backend of your choice:

   For RocksDB:
   ```
   pip install rocksdb
   ```

   For LevelDB:
   ```
   pip install plyvel
   ```

   For both (recommended):
   ```
   pip install rocksdb plyvel
   ```

4. Set up the directory structure:
   ```
   mkdir -p data/default/files
   mkdir -p data/default/luarocks
   mkdir plugins
   ```

## Usage

### CLI Interface

Start the CLI with your preferred storage backend:

```
python cli.py --storage auto  # Tries RocksDB first, falls back to LevelDB
# or
python cli.py --storage rocksdb  # Explicitly use RocksDB
# or
python cli.py --storage leveldb  # Explicitly use LevelDB
```

### Server Interface

Start the server with your preferred storage backend:

```
python server.py --storage auto --host 0.0.0.0 --port 5000
# or
python server.py --storage rocksdb --host 0.0.0.0 --port 5000
# or
python server.py --storage leveldb --host 0.0.0.0 --port 5000
```

### Basic Operations

1. Create a user and log in:
   ```
   create_user username password
   login username password
   ```

2. Create a namespace:
   ```
   create_namespace my_namespace
   use my_namespace
   ```

3. Execute Lua queries:
   ```
   query return db:put("key", "value")
   query return db:get("key")
   ```

## Using LuaRocks Packages in Queries

Liath now supports the use of LuaRocks packages in your Lua queries. Here's how you can use them:

1. Install a LuaRocks package for a specific namespace:
   ```
   luarocks install --tree=./data/namespaces/your_namespace_name package_name
   ```

2. In your Lua query, use the `db:require()` function to load the package:
   ```lua
   local json = db:require("cjson")
   local encoded = json.encode({key = "value"})
   return encoded
   ```

3. You can now use the functions provided by the package in your query.

Note: The `db:require()` function will first look for packages in the namespace-specific directory, and then in the global LuaRocks directory.

### Example: Using the `luasocket` package

1. Install `luasocket` for a namespace:
   ```
   luarocks install --tree=./data/namespaces/my_namespace luasocket
   ```

2. Use it in a query:
   ```lua
   local http = db:require("socket.http")
   local body, code = http.request("http://example.com")
   return {body = body, status_code = code}
   ```

## Pluggable Storage System

Liath supports both RocksDB and LevelDB as storage backends. The choice of backend can affect performance and available features:

- **RocksDB**: Generally offers better performance for larger datasets and supports more advanced features like column families and transactions.
- **LevelDB**: Simpler and may be easier to deploy in some environments. Does not support column families or transactions.

Choose the storage engine that best fits your use case and deployment environment.

## Extending Liath

Liath's plugin architecture allows for easy extension of functionality. To create a new plugin:

1. Create a new Python file in the `plugins` directory.
2. Define a class that inherits from `PluginBase`.
3. Implement the required methods: `initialize`, `get_lua_interface`, and `name`.

For more detailed information on creating plugins, refer to the developer documentation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.