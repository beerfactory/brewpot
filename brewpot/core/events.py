import logging
from concurrent.futures import ThreadPoolExecutor

class Event(object):
    def __init__(self, event_type):
        self._event_type = event_type

    def get_type(self):
        return self._event_type


class EventDispatcher(object):
    def __init__(self, framework):
        self._connected_callbacks = {}
        self._thread_executor = ThreadPoolExecutor(max_workers=10)
        self._framework = framework
        self._logger = self._framework.get_context().get_logger().getChild("EventDispatcher")
        pass

    def send(self, event, async=False):
        self._logger.debug("Event '%s' sent from '%s'", event.get_type(), event.source)
        assert isinstance(event, Event), \
            "Sent event must be sublass of Event class."
        callbacks = []
        try:
            callbacks = self._connected_callbacks[event.get_type]
        except KeyError:
            self._logger.debug("No callback registered for event '%s'",
                event.get_type())

        for r in callbacks:
            if async:
                self._thread_executor.submit(r, event)
            else:
                r(event)

    def register(self, callback, event_types=[]):
        """
        Register a callback which should be called on given event types
        """
        #Check callback is callable
        assert callable(callback), \
            "Event callbacks must be callable."
        for event_type in event_types:
            cb_list = None
            try:
                cb_list = self._connected_callbacks[event_type]
            except Exception:
                cb_list = []
                self._connected_callbacks[event_type] = cb_list
            cb_list.add(callback)

    def unregister(self, callback, event_types=[]):
        """
        Unregister a callback from given event_types or all event types
        """
        if event_types is None or event_types == []:
            event_type = self._connected_callbacks.keys()
        for event_type in event_types:
            if callback in self._connected_callbacks[event_type]:
                self._connected_callbacks[event_type].remove(callback)