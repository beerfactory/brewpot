from core.events import Event


class PluginEvent(Event):
    """
    Base class for event sent from inside plugins.

    PluginEvent holds a reference to the plugin which send the event
    """
    def __init__(self, plugin):
        super(PluginEvent, self).__init__()
        self._plugin = plugin


class FrameworkStartedEvent(PluginEvent):
    """
    Event sent by the framework when start finishes
    """
    def __init__(self, framework):
        super(FrameworkStartedEvent, self).__init__(framework)


class PluginInstalledEvent(PluginEvent):
    """
    Event sent by the framework when a plugin has been installed

    the event holds a reference to the framework and the Plugin
    being installed
    """
    def __init__(self, framework, plugin):
        super(FrameworkStartedEvent, self).__init__(framework)
        self.installed_plugin = plugin


class PluginResolvedEvent(PluginEvent):
    """
    Event sent by the framework when a plugin has been resolved

    the event holds a reference to the framework and the Plugin
    being resolved
    """
    def __init__(self, framework, plugin):
        super(FrameworkStartedEvent, self).__init__(framework)
        self.resolved_plugin = plugin
