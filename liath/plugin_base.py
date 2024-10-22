from abc import ABC, abstractmethod
from lupa import unpacks_lua_table

class PluginBase(ABC):
    @abstractmethod
    def initialize(self, context):
        pass

    @abstractmethod
    def get_lua_interface(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @staticmethod
    def lua_callable(func):
        @unpacks_lua_table
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper