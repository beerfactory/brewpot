import logging
import uuid
from concurrent.futures import ThreadPoolExecutor


class Event(object):
    def __init__(self, ptype):
        self.type = ptype
        self.sender = None
        self.uid = uuid.uuid4()


class EventDispatcher(object):
    def __init__(self, framework):
        self._connected_callbacks = {}
        self._thread_executor = ThreadPoolExecutor(max_workers=10)
        self._framework = framework
        self._logger = self._framework.get_context().get_logger().getChild("EventDispatcher")
        pass

    def send(self, event, async=False):
        if self._logger.isEnabledFor(logging.DEBUG):
            try:
                self._logger.debug("Event '%s' (uid=%s) sent from '%s'", event.type, str(event.uid), event.sender.get_plugin().get_name())
            except:
                self._logger.debug("Event '%s' (uid=%s) sent from '%s'", event.type, str(event.uid), event.sender)
        assert isinstance(event, Event), \
            "Sent event must be sublass of Event class."
        callbacks = []
        try:
            callbacks = self._connected_callbacks[event.type]
        except KeyError:
            self._logger.debug("No callback registered for event '%s'",
                event.type)

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
