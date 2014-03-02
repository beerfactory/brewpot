import logging
from brewpot.utils import enum
from brewpot.utils.logging import PluginLogFilter
from brewpot.core.events import Event

PluginState = enum(
    INSTALLED=0x02,
    RESOLVED=0x04,
    STARTING=0x08,
    STOPPING=0x10,
    ACTIVE=0x20)

class PluginEvent(Event):
    """
    Base class for event sent from inside plugins.

    PluginEvent holds a reference to the plugin which send the event
    """
    def __init__(self, plugin):
        super(PluginEvent, self).__init__()
        self._plugin = plugin


class PluginContext(object):
    def __init__(self, engine, plugin):
        self._plugin = plugin
        self._engine = engine

        #Init logger for plugin
        plugin_name = self._plugin.name
        self._logger = logging.getLogger(plugin_name)
        self._logger.addFilter(PluginLogFilter(self))

    def install_plugin(self, name, path=None):
        return self._engine.install_plugin(name, path)

    def send_event(self, event, async=False):
        self._engine.send_event(self, event, async)

    def register_event_callback(self, callback, event_types):
        self._engine.register_event_callback(self, callback, event_types)

    def get_plugin(self):
        return self._plugin

    def get_logger(self):
        """
        Get a logger initialized with plugin context
        """
        return self._logger


class Plugin(object):

    def __init__(self, engine, plugin_id, name):
        self._state = PluginState.INSTALLED
        self._engine = engine
        self._id = plugin_id
        self.name = name
        self._context = PluginContext(engine, self)

    def get_property(self, key):
        return self._engine.get_property(key)

    def get_context(self):
        return self._context

    def start(self):
        self._state = PluginState.STARTING

    @property
    def state(self):
        """
        Get plugin state
        """
        return self._state
