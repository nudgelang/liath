try:
    import rocksdb
except:
    print("Please install the 'rocksdb' package")
    
from .base import StorageBase

class RocksDBStorage(StorageBase):
    def __init__(self, path, options=None):
        if options is None:
            opts = rocksdb.Options()
            opts.create_if_missing = True
            opts.max_open_files = 300000
            opts.write_buffer_size = 67108864
            opts.max_write_buffer_number = 3
            opts.target_file_size_base = 67108864

            opts.table_factory = rocksdb.BlockBasedTableFactory(
                filter_policy=rocksdb.BloomFilterPolicy(10),
                block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
                block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)))

            opts.compression = rocksdb.CompressionType.lz4_compression
            opts.compaction_style = rocksdb.CompactionStyle.level
        self.db = rocksdb.DB(path, options)
        self.column_families = {}

    def get(self, key):
        return self.db.get(key)

    def put(self, key, value):
        return self.db.put(key, value)

    def delete(self, key):
        return self.db.delete(key)

    def iterator(self):
        return self.db.iteritems()

    def write_batch(self, operations):
        batch = rocksdb.WriteBatch()
        for op in operations:
            if op['type'] == 'put':
                batch.put(op['key'], op['value'])
            elif op['type'] == 'delete':
                batch.delete(op['key'])
        return self.db.write(batch)

    def create_column_family(self, name):
        cf_opts = rocksdb.ColumnFamilyOptions()
        self.column_families[name] = self.db.create_column_family(cf_opts, name)

    def drop_column_family(self, name):
        if name in self.column_families:
            self.db.drop_column_family(self.column_families[name])
            del self.column_families[name]

    def list_column_families(self):
        return list(self.column_families.keys())

    def get_cf(self, cf_name, key):
        if cf_name in self.column_families:
            return self.db.get(key, column_family=self.column_families[cf_name])
        raise ValueError(f"Column family '{cf_name}' not found")

    def put_cf(self, cf_name, key, value):
        if cf_name in self.column_families:
            return self.db.put(key, value, column_family=self.column_families[cf_name])
        raise ValueError(f"Column family '{cf_name}' not found")

    def delete_cf(self, cf_name, key):
        if cf_name in self.column_families:
            return self.db.delete(key, column_family=self.column_families[cf_name])
        raise ValueError(f"Column family '{cf_name}' not found")

    def compact_range(self, begin, end):
        return self.db.compact_range(begin, end)

    def flush(self):
        return self.db.flush()

    def close(self):
        del self.db