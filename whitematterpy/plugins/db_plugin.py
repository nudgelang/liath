from plugin_base import PluginBase
import rocksdb
import json

class DBPlugin(PluginBase):
    def initialize(self, context):
        self.db = context['db']
        self.txn = None
        self.column_families = {}

    def get_lua_interface(self):
        return {
            'get': self.get,
            'put': self.put,
            'delete': self.delete,
            'begin_transaction': self.begin_transaction,
            'commit_transaction': self.commit_transaction,
            'rollback_transaction': self.rollback_transaction,
            'create_column_family': self.create_column_family,
            'drop_column_family': self.drop_column_family,
            'list_column_families': self.list_column_families,
            'get_cf': self.get_cf,
            'put_cf': self.put_cf,
            'delete_cf': self.delete_cf,
            'iterator': self.create_iterator,
            'write_batch': self.write_batch,
            'get_property': self.get_property,
            'compact_range': self.compact_range,
            'flush': self.flush,
        }

    def _encode(self, value):
        return json.dumps(value).encode()

    def _decode(self, value):
        return json.loads(value.decode())

    def get(self, key):
        value = self.db.get(self._encode(key))
        return self._decode(value) if value else None

    def put(self, key, value):
        self.db.put(self._encode(key), self._encode(value))
        return json.dumps({"status": "success"})

    def delete(self, key):
        self.db.delete(self._encode(key))
        return json.dumps({"status": "success"})

    def begin_transaction(self):
        self.txn = self.db.transaction()
        return json.dumps({"status": "success", "message": "Transaction began"})

    def commit_transaction(self):
        if self.txn:
            self.txn.commit()
            self.txn = None
            return json.dumps({"status": "success", "message": "Transaction committed"})
        return json.dumps({"status": "error", "message": "No active transaction"})

    def rollback_transaction(self):
        if self.txn:
            self.txn.rollback()
            self.txn = None
            return json.dumps({"status": "success", "message": "Transaction rolled back"})
        return json.dumps({"status": "error", "message": "No active transaction"})

    def create_column_family(self, name):
        if name not in self.column_families:
            cf_opts = rocksdb.ColumnFamilyOptions()
            self.column_families[name] = self.db.create_column_family(cf_opts, name)
            return json.dumps({"status": "success", "message": f"Column family '{name}' created"})
        return json.dumps({"status": "error", "message": f"Column family '{name}' already exists"})

    def drop_column_family(self, name):
        if name in self.column_families:
            self.db.drop_column_family(self.column_families[name])
            del self.column_families[name]
            return json.dumps({"status": "success", "message": f"Column family '{name}' dropped"})
        return json.dumps({"status": "error", "message": f"Column family '{name}' not found"})

    def list_column_families(self):
        return json.dumps(list(self.column_families.keys()))

    def get_cf(self, cf_name, key):
        if cf_name in self.column_families:
            value = self.db.get(self._encode(key), column_family=self.column_families[cf_name])
            return self._decode(value) if value else None
        return json.dumps({"status": "error", "message": f"Column family '{cf_name}' not found"})

    def put_cf(self, cf_name, key, value):
        if cf_name in self.column_families:
            self.db.put(self._encode(key), self._encode(value), column_family=self.column_families[cf_name])
            return json.dumps({"status": "success"})
        return json.dumps({"status": "error", "message": f"Column family '{cf_name}' not found"})

    def delete_cf(self, cf_name, key):
        if cf_name in self.column_families:
            self.db.delete(self._encode(key), column_family=self.column_families[cf_name])
            return json.dumps({"status": "success"})
        return json.dumps({"status": "error", "message": f"Column family '{cf_name}' not found"})

    def create_iterator(self, cf_name=None):
        if cf_name and cf_name in self.column_families:
            it = self.db.iteritems(self.column_families[cf_name])
        else:
            it = self.db.iteritems()
        return json.dumps([{self._decode(k): self._decode(v)} for k, v in it])

    def write_batch(self, operations):
        batch = rocksdb.WriteBatch()
        for op in operations:
            if op['type'] == 'put':
                batch.put(self._encode(op['key']), self._encode(op['value']))
            elif op['type'] == 'delete':
                batch.delete(self._encode(op['key']))
        self.db.write(batch)
        return json.dumps({"status": "success", "message": f"{len(operations)} operations executed in batch"})

    def get_property(self, property_name):
        value = self.db.get_property(property_name.encode())
        return json.dumps({"value": value.decode() if value else None})

    def compact_range(self, begin=None, end=None):
        self.db.compact_range(self._encode(begin) if begin else None, self._encode(end) if end else None)
        return json.dumps({"status": "success", "message": "Compaction completed"})

    def flush(self):
        self.db.flush()
        return json.dumps({"status": "success", "message": "Database flushed"})

    @property
    def name(self):
        return "db"