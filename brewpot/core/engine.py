import sys
import importlib
import threading

from brewpot import constants
from brewpot.core.exceptions import PluginException
from brewpot.core.events import EventDispatcher
from brewpot.core.plugin import Plugin, PluginEvent, states


engines = []


def newEngine(configuration):
    eng = Engine(configuration)
    engines.append(eng)
    return eng


class EngineStartedEvent(PluginEvent):
    """
    Event sent by the engine when start finishes
    """
    def __init__(self, engine):
        super(EngineStartedEvent, self).__init__(engine)


class PluginInstalledEvent(PluginEvent):
    """
    Event sent by the engine when a plugin has been installed

    the event holds a reference to the engine and the Plugin
    being installed
    """
    def __init__(self, engine, plugin):
        super(EngineStartedEvent, self).__init__(engine)
        self.installed_plugin = plugin


class PluginResolvedEvent(PluginEvent):
    """
    Event sent by the engine when a plugin has been resolved

    the event holds a reference to the engine and the Plugin
    being resolved
    """
    def __init__(self, engine, plugin):
        super(EngineStartedEvent, self).__init__(engine)
        self.resolved_plugin = plugin

class Engine(Plugin):

    def __init__(self, properties):
        """
        Sets up the engine.

        :param properties: The engine properties
        """
        super(Engine, self).__init__(self, constants.SYSTEM_PLUGIN_NAME)
        self.context._plugin_id = 0
        self._logger = self.context.get_logger()

        # Engine properties
        if not isinstance(properties, dict):
            self._properties = {}
        else:
            self._properties = properties.copy()

        #Init engine plugin UUID
        self._properties[constants.PROP_UID] = str(self.uid)

        # Next plugin Id (start at 1, as 0 is reserved for the engine itself)
        self._next_plugin_id = 1

        #Plugins dict pluginId->plugin
        self._plugins = {}
        self._plugins_lock = threading.RLock()

        self._event_dispatcher = EventDispatcher(self)
        self._start_level = 0
        self._state = states.STARTING
        self._logger.info("Engine successfully created")

    def _send_engine_event(self, event, async):
        self.send_event(self.context, event, async)

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
        self._state = states.STARTED

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
            plugin_id = self._next_plugin_id
            new_plugin = Plugin(self, plugin_id, name)
            self._plugins[plugin_id] = new_plugin
            self._next_plugin_id += 1

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
            plugin._state = states.RESOLVED
            self._send_engine_event(
                PluginResolvedEvent(self, plugin),
                async=True)
        except ImportError as ex:
            # Error importing the module
            raise PluginException(
                "Error installing plugin {0}: {1}".format(plugin.name, ex))
