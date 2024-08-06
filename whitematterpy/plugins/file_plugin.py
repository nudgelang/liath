from plugin_base import PluginBase
import os

class FilePlugin(PluginBase):
    def initialize(self, context):
        self.namespace = context['namespace']
        self.data_dir = os.path.join('data', self.namespace, 'files')
        os.makedirs(self.data_dir, exist_ok=True)

    def get_lua_interface(self):
        return {
            'read': self.read,
            'write': self.write,
            'delete': self.delete
        }

    def read(self, filename):
        file_path = os.path.join(self.data_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read()
        return None

    def write(self, filename, content):
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)

    def delete(self, filename):
        file_path = os.path.join(self.data_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    @property
    def name(self):
        return "file"