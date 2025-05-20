# Liath Features Documentation

This document provides detailed information about Liath's key features and capabilities.

## 🔌 Pluggable Storage

Liath supports multiple storage backends, allowing you to choose the one that best fits your needs:

### RocksDB
- High-performance storage engine
- Supports column families
- ACID transactions
- Better for larger datasets
- Advanced features like compression and bloom filters

### LevelDB
- Simpler architecture
- Lower resource requirements
- Good for smaller datasets
- Easier deployment
- Basic key-value operations

## 📝 Lua Query Language

Liath uses Lua as its query language, providing:

- Familiar syntax for Lua developers
- Full access to Lua's standard library
- Custom functions and modules
- Support for complex data structures
- Error handling and debugging capabilities

## 🧩 Plugin Architecture

Extend Liath's functionality through plugins:

- Create custom Python plugins
- Add new Lua functions
- Implement custom storage backends
- Add authentication providers
- Create custom monitoring solutions

## 🔍 Vector Search

Built-in vector database capabilities:

- Store and search vector embeddings
- Support for multiple vector dimensions
- Efficient similarity search
- Integration with embedding models
- Custom distance metrics

## 🤖 AI Integration

Direct access to language models:

- Text generation
- Completion tasks
- Question answering
- Text summarization
- Code generation
- Custom model integration

## 📊 Embedding Generation

Create and manage text embeddings:

- Multiple embedding models
- Batch processing
- Custom embedding dimensions
- Caching support
- Integration with vector search

## 📁 File Operations

Built-in file storage and retrieval:

- Store files in the database
- Version control
- Metadata management
- Streaming support
- Compression options

## 🏷️ Namespaces

Isolate data and operations:

- Separate data storage
- Independent configurations
- Custom plugins per namespace
- Access control
- Resource limits

## 💾 Transaction Support

ACID compliant transactions (RocksDB):

- Atomic operations
- Consistency guarantees
- Isolation levels
- Durability
- Rollback support

## 🔐 User Authentication

Secure user management:

- User creation and deletion
- Password hashing
- Role-based access control
- Session management
- API key support

## 🌐 CLI & HTTP API

Multiple ways to interact:

### CLI Interface
- Interactive shell
- Command history
- Auto-completion
- Script support
- Output formatting

### HTTP API
- RESTful endpoints
- JSON responses
- Authentication
- Rate limiting
- CORS support

## 💾 Backup & Restore

Data protection features:

- Full database backups
- Incremental backups
- Point-in-time recovery
- Backup verification
- Automated scheduling

## ⚡ Query Caching

Performance optimization:

- Result caching
- Cache invalidation
- Memory management
- Cache statistics
- Custom cache policies

## 📈 Monitoring

System performance tracking:

- Query performance metrics
- Resource usage
- Error tracking
- Custom metrics
- Alerting system

## 🔄 Connection Pooling

High concurrency support:

- Connection management
- Pool configuration
- Load balancing
- Connection limits
- Timeout handling

## Getting Started

To learn more about implementing these features, check out our [examples](examples/) directory and [documentation](docs/).

## Contributing

We welcome contributions to improve these features! See our [contributing guide](CONTRIBUTING.md) for more information. 