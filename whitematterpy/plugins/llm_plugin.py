from plugin_base import PluginBase
from llama_cpp import Llama

class LLMPlugin(PluginBase):
    def initialize(self, context):
        self.llm = Llama(model_path="path/to/model.gguf")

    def get_lua_interface(self):
        return {
            'complete': self.complete,
            'chat': self.chat
        }

    def complete(self, prompt):
        return self.llm(prompt, max_tokens=100)

    def chat(self, messages):
        return self.llm.create_chat_completion(messages)

    @property
    def name(self):
        return "llm"