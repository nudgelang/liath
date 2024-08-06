from plugin_base import PluginBase
from usearch.index import Index
import json
import pickle

class VDBPlugin(PluginBase):
    def initialize(self, context):
        self.namespace = context['namespace']
        self.db = context['db']
        self.index = self._load_or_create_index()

    def get_lua_interface(self):
        return {
            'add': self.add,
            'search': self.search,
            'remove': self.remove,
            'count': self.count,
            'clear': self.clear
        }

    def _load_or_create_index(self):
        index_key = f"vdb_index_{self.namespace}".encode()
        serialized_index = self.db.get(index_key)
        if serialized_index:
            return pickle.loads(serialized_index)
        else:
            return Index(ndim=384, metric='cos')

    def _save_index(self):
        index_key = f"vdb_index_{self.namespace}".encode()
        serialized_index = pickle.dumps(self.index)
        self.db.put(index_key, serialized_index)

    def add(self, key, vector):
        self.index.add(key, vector)
        self._save_index()
        return json.dumps({"status": "success", "message": f"Vector added for key: {key}"})

    def search(self, vector, k):
        results = self.index.search(vector, k)
        return json.dumps([{"key": r.key, "distance": r.distance} for r in results])

    def remove(self, key):
        try:
            self.index.remove(key)
            self._save_index()
            return json.dumps({"status": "success", "message": f"Vector removed for key: {key}"})
        except KeyError:
            return json.dumps({"status": "error", "message": f"Key not found: {key}"})

    def count(self):
        return json.dumps({"count": len(self.index)})

    def clear(self):
        self.index = Index(ndim=384, metric='cos')
        self._save_index()
        return json.dumps({"status": "success", "message": "Vector database cleared"})

    @property
    def name(self):
        return "vdb"