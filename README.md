# WhiteMatter

WhiteMatter is an advanced, extensible database system built on top of RocksDB with Lua as its query language. It combines the power of key-value storage, vector search, LLM capabilities, and file operations into a flexible and modular architecture.

## Features

- **RocksDB Backend**: Efficient and reliable storage engine
- **Lua Query Language**: Flexible and powerful querying capabilities
- **Plugin Architecture**: Easily extensible with custom plugins
- **Vector Database**: Built-in vector search capabilities
- **LLM Integration**: Direct access to language models for text generation and completion
- **Embedding Generation**: Create embeddings for text data
- **File Operations**: Built-in file storage and retrieval
- **Namespaces**: Isolate data and operations in separate namespaces
- **Transaction Support**: ACID compliant transactions
- **User Authentication**: Basic user management and authentication
- **CLI and Server Interfaces**: Interact via command line or HTTP API

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/whitematter.git
   cd whitematter
   ```

2. Install the required dependencies:
   ```
   pip install rocksdb lupa flask llama-cpp-python fastembed usearch
   ```

3. Install LuaRocks:
   ```
   sudo apt-get install luarocks  # For Ubuntu/Debian
   # or
   brew install luarocks  # For macOS
   ```

4. Set up the directory structure:
   ```
   mkdir -p data/default/files
   mkdir -p data/default/luarocks
   mkdir plugins
   ```

5. Download a suitable GGUF model for llama_cpp and update the `model_path` in the `LLMPlugin` class.

## Usage

### CLI Interface

1. Start the CLI:
   ```
   python cli.py
   ```

2. Create a user and log in:
   ```
   create_user username password
   login username password
   ```

3. Create a namespace (or use the default one):
   ```
   create_namespace my_namespace
   use my_namespace
   ```

4. Execute Lua queries:
   ```
   query db:put("key1", "value1")
   query local value = db:get("key1"); print(value)
   ```

### Server Interface

1. Start the server:
   ```
   python server.py
   ```

2. Interact with the server using HTTP requests:
   ```
   curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"username":"your_username", "password":"your_password"}'
   
   curl -X POST http://localhost:5000/query -H "Content-Type: application/json" -d '{"namespace":"my_namespace", "query":"db:put(\"key1\", \"value1\"); return db:get(\"key1\")"}'
   ```

## Plugin System

WhiteMatter uses a plugin architecture for extensibility. Plugins are automatically loaded from the `plugins` directory. To create a new plugin:

1. Create a new Python file in the `plugins` directory (e.g., `my_plugin.py`).
2. Define a class that inherits from `PluginBase`.
3. Implement the required methods: `initialize`, `get_lua_interface`, and `name`.

Example:

```python
from plugin_base import PluginBase

class MyPlugin(PluginBase):
    def initialize(self, context):
        # Initialize your plugin
        pass

    def get_lua_interface(self):
        return {
            'my_function': self.my_function
        }

    def my_function(self, arg):
        # Implement your function
        return f"Hello, {arg}!"

    @property
    def name(self):
        return "my_plugin"
```

Your plugin will be automatically loaded and its functions will be available in Lua queries:

```lua
local result = my_plugin:my_function("World")
print(result)  -- Outputs: Hello, World!
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.