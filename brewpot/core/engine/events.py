from brewpot.core.events import Event


class PluginEvent(Event):
    """
    Base class for event sent from inside plugins.

    PluginEvent holds a reference to the plugin which send the event
    """
    def __init__(self, plugin):
        super(PluginEvent, self).__init__()
        self._plugin = plugin


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
