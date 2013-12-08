import sys
import uuid
import importlib
import threading
import logging
from utils import enum
import constants
from core.exceptions import PluginException
from core.events import EventDispatcher
from core.events import Event


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


class PluginLogFilter(logging.Filter):
    """
    Logger filter which adds contextual information
    to logged records :

    * plugin_name : Name of the plugin
    """

    def __init__(self, context):
        logging.Filter.__init__(self)
        self._context = context

    def filter(self, record):
        record.plugin_name = self._context.get_plugin().get_name()
        return record


class PluginContext(object):
    def __init__(self, framework, plugin):
        self._plugin = plugin
        self._framework = framework

        #Init logger for plugin
        plugin_name = self._plugin.get_name()
        self._logger = logging.getLogger(plugin_name)
        self._logger.addFilter(PluginLogFilter(self))

    def install_plugin(self, name, path=None):
        return self._framework.install_plugin(name, path)

    def send_event(self, event, async=False):
        self._framework.send_event(self, event, async)

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
        self._name = name
        self._context = PluginContext(framework, self)

    def get_property(self, key):
        return self._framework.get_property(key)

    def get_name(self):
        return self._name

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

        self._event_dispatcher = EventDispatcher(self)
        self._start_level = 0
        self._state = PluginState.STARTING
        self._send_framework_event(Event("TEST"), async=True)
        self.get_context().get_logger().info("Framework surceesfully created")

    def _send_framework_event(self, event, async):
        self.send_event(self.get_context(), event, async)

    def send_event(self, source_context, event, async):
        event.source = source_context
        self._event_dispatcher.send(event, async)

    def get_property(self, key):
        return self._properties[key]

    def start(self):
        self.get_context().get_logger().info("Framework starting ...")
        super(Framework, self).start()
        self._state = PluginState.STARTING
        self.get_context().get_logger().info("Framework started")

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
                    "Error installing plugin {0}: {1}".format(name, ex))

            plugin_id = self.__next_plugin_id
            new_plugin = Plugin(self, plugin_id, name)
            self._plugins[plugin_id] = new_plugin
            self.__next_plugin_id += 1

        return new_plugin
