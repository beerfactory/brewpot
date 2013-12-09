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
    def __init__(self, plugin):
        super(FrameworkStartedEvent, self).__init__(plugin)
