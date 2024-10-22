from plugin_base import PluginBase
import json

class DBPlugin(PluginBase):
    def initialize(self, context):
        self.db = context['db']
        self.txn = None

    def get_lua_interface(self):
        return {
            'db_get': self.lua_callable(self.get),
            'db_put': self.lua_callable(self.put),
            'db_delete': self.lua_callable(self.delete),
            'db_begin_transaction': self.lua_callable(self.begin_transaction),
            'db_commit_transaction': self.lua_callable(self.commit_transaction),
            'db_rollback_transaction': self.lua_callable(self.rollback_transaction),
            'db_create_column_family': self.lua_callable(self.create_column_family),
            'db_drop_column_family': self.lua_callable(self.drop_column_family),
            'db_list_column_families': self.lua_callable(self.list_column_families),
            'db_get_cf': self.lua_callable(self.get_cf),
            'db_put_cf': self.lua_callable(self.put_cf),
            'db_delete_cf': self.lua_callable(self.delete_cf),
            'db_iterator': self.lua_callable(self.create_iterator),
            'db_write_batch': self.lua_callable(self.write_batch),
            'db_compact_range': self.lua_callable(self.compact_range),
            'db_flush': self.lua_callable(self.flush),
        }

    def _encode(self, value):
        return json.dumps(value).encode()

    def _decode(self, value):
        return json.loads(value.decode()) if value else None

    def get(self, key):
        value = self.db.get(self._encode(key))
        return self._decode(value)

    def put(self, key, value):
        self.db.put(self._encode(key), self._encode(value))
        return json.dumps({"status": "success"})

    def delete(self, key):
        self.db.delete(self._encode(key))
        return json.dumps({"status": "success"})

    def begin_transaction(self):
        # Note: Transaction support may vary depending on the storage backend
        if hasattr(self.db, 'transaction'):
            self.txn = self.db.transaction()
            return json.dumps({"status": "success", "message": "Transaction began"})
        return json.dumps({"status": "error", "message": "Transactions not supported by this storage backend"})

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
        try:
            self.db.create_column_family(name)
            return json.dumps({"status": "success", "message": f"Column family '{name}' created"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def drop_column_family(self, name):
        try:
            self.db.drop_column_family(name)
            return json.dumps({"status": "success", "message": f"Column family '{name}' dropped"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def list_column_families(self):
        return json.dumps(self.db.list_column_families())

    def get_cf(self, cf_name, key):
        try:
            value = self.db.get_cf(cf_name, self._encode(key))
            return self._decode(value)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def put_cf(self, cf_name, key, value):
        try:
            self.db.put_cf(cf_name, self._encode(key), self._encode(value))
            return json.dumps({"status": "success"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def delete_cf(self, cf_name, key):
        try:
            self.db.delete_cf(cf_name, self._encode(key))
            return json.dumps({"status": "success"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def create_iterator(self, cf_name=None):
        try:
            if cf_name:
                it = self.db.iterator(cf_name)
            else:
                it = self.db.iterator()
            return json.dumps([{self._decode(k): self._decode(v)} for k, v in it])
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def write_batch(self, operations):
        try:
            self.db.write_batch(operations)
            return json.dumps({"status": "success", "message": f"{len(operations)} operations executed in batch"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def compact_range(self, begin=None, end=None):
        try:
            self.db.compact_range(self._encode(begin) if begin else None, self._encode(end) if end else None)
            return json.dumps({"status": "success", "message": "Compaction completed"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def flush(self):
        try:
            self.db.flush()
            return json.dumps({"status": "success", "message": "Database flushed"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def require_package(self, package_name):
        try:
            return self.lua.require(package_name)
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Failed to load package {package_name}: {str(e)}"})

    @property
    def name(self):
        return "db"