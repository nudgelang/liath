from plugin_base import PluginBase
from usearch.index import Index, Matches
import json
import numpy as np
import os

class VDBPlugin(PluginBase):
    def initialize(self, context):
        self.namespace = context['namespace']
        self.db = context['db']
        self.data_dir = context['data_dir']
        self.index_path = os.path.join(self.data_dir, f"{self.namespace}_index.usearch")
        self.index = self._load_or_create_index()

    def get_lua_interface(self):
        return {
            'vdb_create_index': self.lua_callable(self.create_index),
            'vdb_add': self.lua_callable(self.add),
            'vdb_search': self.lua_callable(self.search),
            'vdb_remove': self.lua_callable(self.remove),
            'vdb_count': self.lua_callable(self.count),
            'vdb_clear': self.lua_callable(self.clear),
            'vdb_save': self.lua_callable(self.save_index),
            'vdb_load': self.lua_callable(self.load_index),
            'vdb_get_metadata': self.lua_callable(self.get_metadata)
        }

    def _load_or_create_index(self):
        if os.path.exists(self.index_path):
            return Index.restore(self.index_path)
        else:
            return None  # We'll create the index when the user calls create_index

    def create_index(self, ndim, metric='cos', dtype='f32', connectivity=16, expansion_add=128, expansion_search=64):
        self.index = Index(
            ndim=ndim,
            metric=metric,
            dtype=dtype,
            connectivity=connectivity,
            expansion_add=expansion_add,
            expansion_search=expansion_search
        )
        self.save_index()
        return json.dumps({"status": "success", "message": f"Index created with {ndim} dimensions"})

    def add(self, key, vector):
        if self.index is None:
            return json.dumps({"status": "error", "message": "Index not created. Call vdb_create_index first."})
        self.index.add(key, np.array(vector, dtype=np.float32))
        self.save_index()
        return json.dumps({"status": "success", "message": f"Vector added for key: {key}"})

    def search(self, vector, k):
        if self.index is None:
            return json.dumps({"status": "error", "message": "Index not created. Call vdb_create_index first."})
        matches: Matches = self.index.search(np.array(vector, dtype=np.float32), k)
        return json.dumps([{"key": match.key, "distance": float(match.distance)} for match in matches])

    def remove(self, key):
        if self.index is None:
            return json.dumps({"status": "error", "message": "Index not created. Call vdb_create_index first."})
        try:
            self.index.remove(key)
            self.save_index()
            return json.dumps({"status": "success", "message": f"Vector removed for key: {key}"})
        except KeyError:
            return json.dumps({"status": "error", "message": f"Key not found: {key}"})

    def count(self):
        if self.index is None:
            return json.dumps({"count": 0})
        return json.dumps({"count": len(self.index)})

    def clear(self):
        if self.index is not None:
            self.index = Index(
                ndim=self.index.ndim,
                metric=self.index.metric,
                dtype=self.index.dtype,
                connectivity=self.index.connectivity,
                expansion_add=self.index.expansion_add,
                expansion_search=self.index.expansion_search
            )
            self.save_index()
        return json.dumps({"status": "success", "message": "Vector database cleared"})

    def save_index(self):
        if self.index is not None:
            self.index.save(self.index_path)
            return json.dumps({"status": "success", "message": "Index saved to disk"})
        return json.dumps({"status": "error", "message": "No index to save"})

    def load_index(self):
        if os.path.exists(self.index_path):
            self.index = Index.restore(self.index_path)
            return json.dumps({"status": "success", "message": "Index loaded from disk"})
        return json.dumps({"status": "error", "message": "No index file found"})

    def get_metadata(self):
        if self.index is not None:
            metadata = Index.metadata(self.index_path)
            return json.dumps({
                "ndim": metadata.ndim,
                "metric": metadata.metric,
                "dtype": metadata.dtype,
                "connectivity": metadata.connectivity,
                "expansion_add": metadata.expansion_add,
                "expansion_search": metadata.expansion_search
            })
        return json.dumps({"status": "error", "message": "No index available"})

    @property
    def name(self):
        return "vdb"