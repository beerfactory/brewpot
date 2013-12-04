import uuid
from utils import enum
import constants


PluginState = enum(INSTALLED=0x02, RESOLVED=0x04, STARTING=0x08, STOPPING=0x10, ACTIVE=0x20)

class PluginContext(object):
    def __init__(self, framework, plugin):
        self._plugin = plugin
        pass


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

    def get_symbolic_name(self):
        return self._name

    def get_plugin_context(self):
        return self._context

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

        self._start_level = 0
        self._state = PluginState.STARTING

    def get_property(self, key):
        return self._properties[key]

    def start(self):
        self._state = PluginState.STARTING

class FrameworkFactory(object):
    @classmethod
    def newFramework(cls, configuration):
        if not hasattr(cls, 'frameworks'):
            cls.frameworks = []
        fwk = Framework(configuration)
        cls.frameworks.append(fwk)
        return fwk
