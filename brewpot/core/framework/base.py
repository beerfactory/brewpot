import sys
import uuid
import importlib
import threading
import constants
from core.exceptions import PluginException
from core.events import EventDispatcher
from core.framework.events import FrameworkStartedEvent
from core.framework.plugin import Plugin, PluginState

frameworks = []


def newFramework(configuration):
    fwk = Framework(configuration)
    frameworks.append(fwk)
    return fwk


class Framework(Plugin):

    def __init__(self, properties):
        """
        Sets up the framework.

        :param properties: The framework properties
        """
        super(Framework, self).__init__(self, 0, constants.SYSTEM_PLUGIN_NAME)
        self._logger = self.get_context().get_logger()

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

        self._event_dispatcher = EventDispatcher(self)
        self._start_level = 0
        self._state = PluginState.STARTING
        self._logger.info("Framework surceesfully created")

    def _send_framework_event(self, event, async):
        self.send_event(self.get_context(), event, async)

    def send_event(self, plugin_context, event, async):
        event.sender = plugin_context
        self._event_dispatcher.send(event, async)

    def register_event_callback(self, plugin_context, callback, event_types):
        self._event_dispatcher.register(callback, event_types)

    def get_property(self, key):
        return self._properties[key]

    def start(self):
        self._logger.info("Framework starting ...")

        super(Framework, self).start()
        self._state = PluginState.ACTIVE

        self._send_framework_event(FrameworkStartedEvent(self), async=True)
        self._logger.info("Framework started")

    def install_plugin(self, name, path=None):
        with self._plugins_lock:
            for plugin in self._plugins:
                if plugin.get_name() == name:
                    self._logger.warn("Plugin %s already installed", name)
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
                    "Error installing plugin {0}: {1}".format(name, ex))

            plugin_id = self.__next_plugin_id
            new_plugin = Plugin(self, plugin_id, name)
            self._plugins[plugin_id] = new_plugin
            self.__next_plugin_id += 1

        return new_plugin
