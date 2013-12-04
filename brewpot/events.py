
class Event(object):
    def __init__(self, event_type):
        self._event_type = event_type

    def get_event_type(self):
        return self._event_type