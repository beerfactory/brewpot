import sys
import uuid
import importlib
import threading
from brewpot import constants
from brewpot.core.exceptions import PluginException
from brewpot.core.events import EventDispatcher
from brewpot.core.engine.events import EngineStartedEvent
from brewpot.core.engine.events import PluginInstalledEvent
from brewpot.core.engine.events import PluginResolvedEvent
from brewpot.core.engine.plugin import Plugin, PluginState

frameworks = []


def newEngine(configuration):
    fwk = Engine(configuration)
    frameworks.append(fwk)
    return fwk


class Engine(Plugin):

    def __init__(self, properties):
        """
        Sets up the engine.

        :param properties: The engine properties
        """
        super(Engine, self).__init__(self, 0, constants.SYSTEM_PLUGIN_NAME)
        self._logger = self.get_context().get_logger()

        # Engine properties
        if not isinstance(properties, dict):
            self._properties = {}
        else:
            self._properties = properties.copy()

        #Init engine plugin UUID
        self.uid = uuid.uuid4()
        self._properties[constants.PROP_UID] = str(self.uid)

        # Next plugin Id (start at 1, as 0 is reserved for the engine itself)
        self._next_plugin_id = 1

        #Plugins dict pluginId->plugin
        self._plugins = {}
        self._plugins_lock = threading.RLock()

        self._event_dispatcher = EventDispatcher(self)
        self._start_level = 0
        self._state = PluginState.STARTING
        self._logger.info("Engine successfully created")

    def _send_engine_event(self, event, async):
        self.send_event(self.get_context(), event, async)

    def send_event(self, plugin_context, event, async):
        event.sender = plugin_context
        self._event_dispatcher.send(event, async)

    def register_event_callback(self, plugin_context, callback, event_types):
        self._event_dispatcher.register(callback, event_types)

    def get_property(self, key):
        return self._properties[key]

    def start(self):
        self._logger.info("Engine starting ...")

        super(Engine, self).start()
        self._state = PluginState.ACTIVE

        self._send_engine_event(EngineStartedEvent(self), async=True)
        self._logger.info("Engine started")

    def install_plugin(self, name, path=None):
        """
        Install a plugin

        Plugin is added to the engine plugins list. Then the engine
        tries to resolve the plugin (importing module). The plugin is RESOLVED
        if this operation succeed, INSTALLED otherwise.
        """
        with self._plugins_lock:
            plugin_id = self.__next_plugin_id
            new_plugin = Plugin(self, plugin_id, name)
            self._plugins[plugin_id] = new_plugin
            self.__next_plugin_id += 1

        for plugin in self._plugins:
            if plugin.name == name:
                self._logger.warn("Plugin %s already installed", name)
                return plugin
        self._send_engine_event(
            PluginInstalledEvent(self, plugin),
            async=True)

        try:
            self.resolve_plugin(plugin)
        except PluginException as pe:
            self._logger.warn(
                "Plugin {0} cannot be resolved: {1}".format(name, pe))

    def resolve_plugin(self, plugin, path=None):
        try:
            if path:
                # Insert path
                sys.path.insert(0, path)

            if plugin.name in sys.modules:
                # The module has already been loaded
                module = sys.modules[plugin.name]
            else:
                # Load the module
                module = importlib.import_module(plugin.name)
                sys.modules[plugin.name] = module
            plugin._state = PluginState.RESOLVED
            self._send_engine_event(
                PluginResolvedEvent(self, plugin),
                async=True)
        except ImportError as ex:
            # Error importing the module
            raise PluginException(
                "Error installing plugin {0}: {1}".format(plugin.name, ex))
