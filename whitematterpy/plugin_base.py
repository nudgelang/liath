from abc import ABC, abstractmethod

class PluginBase(ABC):
    @abstractmethod
    def initialize(self, context):
        """
        Initialize the plugin with the given context.
        The context object will contain references to the database and other necessary components.
        """
        pass

    @abstractmethod
    def get_lua_interface(self):
        """
        Return a dictionary of functions that will be exposed to the Lua environment.
        """
        pass

    @property
    @abstractmethod
    def name(self):
        """
        Return the name of the plugin. This will be used as the key in the Lua environment.
        """
        pass