from plugin_base import PluginBase
from usearch.index import Index

class VDBPlugin(PluginBase):
    def initialize(self, context):
        self.namespace = context['namespace']
        self.index = Index(ndim=384, metric='cos')

    def get_lua_interface(self):
        return {
            'add': self.add,
            'search': self.search
        }

    def add(self, key, vector):
        self.index.add(key, vector)

    def search(self, vector, k):
        return self.index.search(vector, k)

    @property
    def name(self):
        return "vdb"