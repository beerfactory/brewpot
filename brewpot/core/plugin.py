import logging
import uuid
from brewpot.utils.logging import PluginLogFilter
from brewpot.core.events import Event

class _PluginStateEnum(object):
    class State(object):
        name = None

        def __repr__(self):
            return "state.%s" % self.name

    def __setattr__(self, key, value):
        if isinstance(value, self.State):
            value.name = key
        object.__setattr__(self, key, value)


states = _PluginStateEnum()
states.INITIALIZED = states.State()
states.INSTALLED = states.State()
states.STARTING = states.State()
states.STARTED = states.State()
states.STOPPING = states.State()
states.STOPPED = states.State()


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
        self._plugin_id = None

        #Init logger for plugin
        plugin_name = self._plugin.name
        self._logger = logging.getLogger(plugin_name)
        self._logger.addFilter(PluginLogFilter(self))

    @property
    def plugin_id(self):
        return self._plugin_id

    def send_event(self, event, async=False):
        self._plugin._engine.send_event(self, event, async)

    def register_event_callback(self, callback, event_types):
        self._plugin._engine.register_event_callback(self, callback, event_types)

    def get_plugin(self):
        return self._plugin

    def get_logger(self):
        """
        Get a logger initialized with plugin context
        """
        return self._logger


class Plugin(object):

    def __init__(self, engine, name=None):

        self.name = name
        if name == None:
            self.name = __qualname__

        self.engine = engine
        self.uid = uuid.uuid4()
        self._context = PluginContext(self.engine, self)
        self._state = states.INITIALIZED

    def get_property(self, key):
        return self._engine.get_property(key)

    @property
    def context(self):
        return self._context

    def start(self):
        self._state = states.STARTING

    @property
    def state(self):
        """
        Get plugin state
        """
        return self._state
