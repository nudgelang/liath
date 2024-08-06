from plugin_base import PluginBase
import pandas as pd
import json
from fastembed import (
    SparseTextEmbedding,
    TextEmbedding,
    LateInteractionTextEmbedding,
    ImageEmbedding,
)

class EmbedPlugin(PluginBase):
    def initialize(self, context):
        self.embedding_types = {
            "text": TextEmbedding,
            "sparse_text": SparseTextEmbedding,
            "late_interaction_text": LateInteractionTextEmbedding,
            "image": ImageEmbedding
        }
        self.current_type = "text"
        self.current_model = "BAAI/bge-small-en-v1.5"  # Default model
        self.embedding_model = self.embedding_types[self.current_type](model_name=self.current_model)

    def get_lua_interface(self):
        return {
            'embed': self.embed,
            'list_supported_models': self.list_supported_models,
            'set_model': self.set_model,
            'set_embedding_type': self.set_embedding_type,
            'get_current_config': self.get_current_config
        }

    def embed(self, input_data):
        try:
            if self.current_type == "image":
                # Assuming input_data is a path to an image file
                return next(self.embedding_model.embed([input_data]))
            else:
                return next(self.embedding_model.embed([input_data]))
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_supported_models(self):
        supported_models = (
            pd.DataFrame(TextEmbedding.list_supported_models())
            .sort_values("size_in_GB")
            .drop(columns=["sources", "model_file", "additional_files"])
            .reset_index(drop=True)
        )
        return json.dumps(supported_models.to_dict(orient="records"))

    def set_model(self, model_name):
        try:
            self.current_model = model_name
            self.embedding_model = self.embedding_types[self.current_type](model_name=self.current_model)
            return json.dumps({"status": "success", "message": f"Model set to {model_name}"})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def set_embedding_type(self, embedding_type):
        if embedding_type in self.embedding_types:
            self.current_type = embedding_type
            self.embedding_model = self.embedding_types[self.current_type](model_name=self.current_model)
            return json.dumps({"status": "success", "message": f"Embedding type set to {embedding_type}"})
        else:
            return json.dumps({"status": "error", "message": f"Invalid embedding type. Choose from {list(self.embedding_types.keys())}"})

    def get_current_config(self):
        return json.dumps({
            "current_type": self.current_type,
            "current_model": self.current_model
        })

    @property
    def name(self):
        return "embed"