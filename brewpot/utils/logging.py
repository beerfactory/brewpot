import logging


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
        record.plugin_name = self._context.get_plugin().name
        return record
