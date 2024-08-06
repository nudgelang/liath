import rocksdb
from lupa import LuaRuntime, lua_type
import json
import yaml
import os
import threading
import importlib.util
import inspect
from plugin_base import PluginBase
from storage.rocksdb_storage import RocksDBStorage
from storage.leveldb_storage import LevelDBStorage

class Database:
    def __init__(self, data_dir='./data', plugins_dir='./plugins', storage_type='auto'):
        self.data_dir = data_dir
        self.plugins_dir = plugins_dir
        self.namespaces = {}
        self.metadata_file = os.path.join(data_dir, 'metadata.json')
        
        if storage_type == 'auto':
            try:
                import rocksdb
                self.StorageClass = RocksDBStorage
            except ImportError:
                self.StorageClass = LevelDBStorage
        elif storage_type == 'rocksdb':
            self.StorageClass = RocksDBStorage
        elif storage_type == 'leveldb':
            self.StorageClass = LevelDBStorage
        else:
            raise ValueError("Invalid storage_type. Choose 'auto', 'rocksdb', or 'leveldb'")

        self.auth_db = self.StorageClass(os.path.join(data_dir, "auth.db"))
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self._setup_lua_environment()
        self.plugins = self.load_plugins()
        self.load_metadata()

    def _setup_lua_environment(self):
        # Load LuaRocks packages
        self.lua.execute('''
            json = require("cjson")
            yaml = require("lyaml")
            http = require("socket.http")
            ltn12 = require("ltn12")
            htmlparser = require("htmlparser")
            markdown = require("markdown")
        ''')

    def load_plugins(self):
        plugins = {}
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.py'):
                module_name = filename[:-3]
                module_path = os.path.join(self.plugins_dir, filename)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj is not PluginBase:
                        plugin = obj()
                        plugins[plugin.name] = plugin
        return plugins

    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                for name, info in metadata.items():
                    self.create_namespace(name, info['packages'])
        else:
            self.create_namespace('default')

    def save_metadata(self):
        metadata = {name: {'packages': list(info['packages'])} for name, info in self.namespaces.items()}
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f)

    def create_namespace(self, name, packages=None):
        if name not in self.namespaces:
            db_path = os.path.join(self.data_dir, f"{name}.db")
            self.namespaces[name] = {
                'db': self.StorageClass(db_path),
                'lock': threading.Lock(),
                'packages': set(packages or []),
            }
            self.save_metadata()
       
    def execute_query(self, namespace, query, return_format='dict'):
        if namespace not in self.namespaces:
            raise ValueError(f"Namespace '{namespace}' does not exist")

        with self.namespaces[namespace]['lock']:
            context = {
                'namespace': namespace,
                'db': self.namespaces[namespace]['db'],
                'packages': self.namespaces[namespace]['packages']
            }
            
            lua_env = {}
            for plugin_name, plugin in self.plugins.items():
                plugin.initialize(context)
                lua_env[plugin_name] = plugin.get_lua_interface()

            lua_function = self.lua.eval(f"function({', '.join(lua_env.keys())}) {query} end")
            result = lua_function(**lua_env)
            
            return self._format_result(result, return_format)

    def _format_result(self, result, format):
        if format == 'dict':
            return self._lua_to_python(result)
        elif format == 'json':
            return json.dumps(self._lua_to_python(result))
        elif format == 'yaml':
            return yaml.dump(self._lua_to_python(result))
        elif format == 'markdown':
            return self._dict_to_markdown(self._lua_to_python(result))
        else:
            raise ValueError(f"Unsupported return format: {format}")

    def _lua_to_python(self, obj):
        lua_type_name = lua_type(obj)
        if lua_type_name == 'table':
            if len(obj) > 0:
                return [self._lua_to_python(item) for item in obj.values()]
            else:
                return {str(k): self._lua_to_python(v) for k, v in obj.items()}
        elif lua_type_name == 'unicode':
            return str(obj)
        elif lua_type_name in ['int', 'long', 'float']:
            return obj
        elif lua_type_name == 'NoneType':
            return None
        else:
            return str(obj)

    def _dict_to_markdown(self, d, level=0):
        markdown = ""
        for key, value in d.items():
            markdown += "  " * level + f"- **{key}**: "
            if isinstance(value, dict):
                markdown += "\n" + self._dict_to_markdown(value, level + 1)
            elif isinstance(value, list):
                markdown += "\n" + "  " * (level + 1) + "- " + "\n  ".join(str(item) for item in value)
            else:
                markdown += str(value) + "\n"
        return markdown

    def authenticate_user(self, username, password):
        stored_password = self.auth_db.get(username.encode())
        return stored_password == password.encode()

    def create_user(self, username, password):
        if self.auth_db.get(username.encode()) is not None:
            raise ValueError("User already exists")
        self.auth_db.put(username.encode(), password.encode())

    def list_namespaces(self):
        return list(self.namespaces.keys())

    def install_package(self, namespace, package):
        if namespace not in self.namespaces:
            raise ValueError(f"Namespace '{namespace}' does not exist")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                subprocess.run(['luarocks', 'install', package, f'--tree={temp_dir}'], check=True)
                dest_dir = os.path.join(self.data_dir, namespace, 'luarocks')
                os.makedirs(dest_dir, exist_ok=True)
                for item in os.listdir(temp_dir):
                    s = os.path.join(temp_dir, item)
                    d = os.path.join(dest_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
                self.namespaces[namespace]['packages'].add(package)
                self.save_metadata()
                return True
            except subprocess.CalledProcessError:
                return False
            
    def close(self):
        for namespace in self.namespaces.values():
            namespace['db'].close()
        self.auth_db.close()

if __name__ == "__main__":
    db = Database()
    print("Database initialized with namespaces:", db.list_namespaces())
    print("Loaded plugins:", list(db.plugins.keys()))