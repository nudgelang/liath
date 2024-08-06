from plugin_base import PluginBase

class DBPlugin(PluginBase):
    def initialize(self, context):
        self.db = context['db']
        self.txn = None

    def get_lua_interface(self):
        return {
            'get': self.get,
            'put': self.put,
            'delete': self.delete,
            'begin_transaction': self.begin_transaction,
            'commit_transaction': self.commit_transaction,
            'rollback_transaction': self.rollback_transaction
        }

    def get(self, key):
        value = self.db.get(key.encode())
        return value.decode() if value else None

    def put(self, key, value):
        self.db.put(key.encode(), value.encode())

    def delete(self, key):
        self.db.delete(key.encode())

    def begin_transaction(self):
        self.txn = self.db.transaction()

    def commit_transaction(self):
        if self.txn:
            self.txn.commit()
            self.txn = None

    def rollback_transaction(self):
        if self.txn:
            self.txn.rollback()
            self.txn = None

    @property
    def name(self):
        return "db"