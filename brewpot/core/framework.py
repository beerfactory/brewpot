import sys
import uuid
import importlib
import threading
from utils import enum
import constants
from core.exceptions import PluginException


PluginState = enum(
    INSTALLED=0x02,
    RESOLVED=0x04,
    STARTING=0x08,
    STOPPING=0x10,
    ACTIVE=0x20)

frameworks = []


def newFramework(configuration):
    fwk = Framework(configuration)
    frameworks.append(fwk)
    return fwk


class PluginContext(object):
    def __init__(self, framework, plugin):
        self._plugin = plugin
        self._framework = framework
        pass

    def install_plugin(self, name, path=None):
        return self._framework.install_plugin(name, path)


class Plugin(object):

    def __init__(self, framework, plugin_id, name):
        self._state = PluginState.INSTALLED
        self._context = PluginContext(framework, self)
        self._framework = framework
        self._id = plugin_id
        self._name = name
        pass

    def get_property(self, key):
        return self._framework.get_property(key)

    def get_name(self):
        return self._name

    def get_plugin_context(self):
        return self._context

    def start(self):
        self._state = PluginState.STARTING

    @property
    def state(self):
        """
        Get plugin state
        """
        return self._state


class Framework(Plugin):

    def __init__(self, properties):
        """
        Sets up the framework.

        :param properties: The framework properties
        """
        Plugin.__init__(self, self, 0, constants.SYSTEM_PLUGIN_NAME)

        # Framework properties
        if not isinstance(properties, dict):
            self._properties = {}
        else:
            self._properties = properties.copy()

        #Init framework UUID
        self.uid = uuid.uuid4()
        self._properties[constants.PROP_UID] = str(self.uid)

        # Next plugin Id (start at 1, as 0 is reserved for the framework itself)
        self._next_plugin_id = 1

        #Plugins dict pluginId->plugin
        self._plugins = {}
        self._plugins_lock = threading.RLock()

        self._start_level = 0
        self._state = PluginState.STARTING

    def get_property(self, key):
        return self._properties[key]

    def start(self):
        super(Framework, self).start()
        self._state = PluginState.STARTING

    def install_plugin(self, name, path=None):
        with self._plugins_lock:
            for plugin in self._plugins:
                if plugin.get_name() == name:
                    #TODO : Add logging
                    return plugin
            #TODO Load plugin
            try:
                if path:
                    # Insert path
                    sys.path.insert(0, path)

                if name in sys.modules:
                    # The module has already been loaded
                    module = sys.modules[name]
                else:
                    # Load the module
                    module = importlib.import_module(name)
                    sys.modules[name] = module

            except ImportError as ex:
                # Error importing the module
                raise PluginException(
                    "Error installing bundle {0}: {1}".format(name, ex))

            plugin_id = self.__next_bundle_id
            new_plugin = Plugin(self, plugin_id, name)
            self._plugins[plugin_id] = new_plugin
            self.__next_bundle_id += 1

        return new_plugin
