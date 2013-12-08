
class PluginException(Exception):
    """
    The base of all plugin exceptions
    """

    def __init__(self, content):
        if isinstance(content, Exception):
            Exception.__init__(self, str(content))

        else:
            Exception.__init__(self, content)
