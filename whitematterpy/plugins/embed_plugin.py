from plugin_base import PluginBase
from fastembed import TextEmbedding

class EmbedPlugin(PluginBase):
    def initialize(self, context):
        self.embedding_model = TextEmbedding()

    def get_lua_interface(self):
        return {
            'embed': self.embed
        }

    def embed(self, text):
        return next(self.embedding_model.embed([text]))

    @property
    def name(self):
        return "embed"