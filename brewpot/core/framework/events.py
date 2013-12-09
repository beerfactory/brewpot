from core.events import PluginEvent


class FrameworkStartedEvent(PluginEvent):
    def __init__(self, plugin):
        super(FrameworkStartedEvent, self).__init__(plugin)
