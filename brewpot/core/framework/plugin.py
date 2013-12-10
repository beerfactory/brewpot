import logging
from utils import enum
from utils.logging import PluginLogFilter

PluginState = enum(
    INSTALLED=0x02,
    RESOLVED=0x04,
    STARTING=0x08,
    STOPPING=0x10,
    ACTIVE=0x20)


class PluginContext(object):
    def __init__(self, framework, plugin):
        self._plugin = plugin
        self._framework = framework

        #Init logger for plugin
        plugin_name = self._plugin.name
        self._logger = logging.getLogger(plugin_name)
        self._logger.addFilter(PluginLogFilter(self))

    def install_plugin(self, name, path=None):
        return self._framework.install_plugin(name, path)

    def send_event(self, event, async=False):
        self._framework.send_event(self, event, async)

    def register_event_callback(self, callback, event_types):
        self._framework.register_event_callback(self, callback, event_types)

    def get_plugin(self):
        return self._plugin

    def get_logger(self):
        """
        Get a logger initialized with plugin context
        """
        return self._logger


class Plugin(object):

    def __init__(self, framework, plugin_id, name):
        self._state = PluginState.INSTALLED
        self._framework = framework
        self._id = plugin_id
        self.name = name
        self._context = PluginContext(framework, self)

    def get_property(self, key):
        return self._framework.get_property(key)

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
