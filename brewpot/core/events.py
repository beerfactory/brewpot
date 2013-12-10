import logging
import uuid
import time
from concurrent.futures import ThreadPoolExecutor


class Event(object):
    """
    Base class for all events

    This class initializes the event UUID and the
    timestamp when the event was created
    """
    def __init__(self):
        self.uid = uuid.uuid4()
        self._event_time = time.time()


class AnyEvent(Event):
    """
    Special event type for registering callback listening
    for any event type.
    AnyEvent instances should not be sent by sender
    """
    def __init__(self):
        super(AnyEvent, self).__init__()


class EventDispatcher(object):
    def __init__(self, framework):
        self._connected_callbacks = {}
        self._thread_executor = ThreadPoolExecutor(max_workers=10)
        self._framework = framework
        self._logger = self._framework.get_context().get_logger().getChild("EventDispatcher")
        pass

    def send(self, event, async=False):
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                "Event '%s' (uid=%s) sent",
                str(type(event)),
                str(event.uid))
        assert isinstance(event, Event), \
            "Sent event must be sublass of Event class."
        callbacks = []
        try:
            #Send event to callback register to the event type and AnyEvent
            ev_callbacks = self._connected_callbacks[type(event)]
            self._logger.debug(
                "%d callback(s) registered for event '%s'",
                len(ev_callbacks),
                str(type(event)))
            callbacks += ev_callbacks
        except KeyError:
            self._logger.debug(
                "0 callback registered for event '%s'",
                str(type(event)))

        try:
            any_callbacks = self._connected_callbacks[AnyEvent]
            self._logger.debug(
                "%d callback(s) registered for event '%s'",
                len(any_callbacks),
                str(AnyEvent))
            callbacks += any_callbacks
        except KeyError:
            self._logger.debug(
                "0 callback registered for event '%s'",
                str(AnyEvent))

        if len(callbacks) == 0:
            self._logger.warn(
                "No callback registered for sent event %s",
                str(type(event)))
        else:
            self._logger.debug(
                "Sending %s event to %d callback(s)",
                str(type(event)),
                len(callbacks))
        for r in callbacks:
            event._callback_time = time.time()
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
            cb_list.append(callback)

    def unregister(self, callback, event_types=[]):
        """
        Unregister a callback from given event_types or all event types
        """
        if event_types is None or event_types == []:
            event_type = self._connected_callbacks.keys()
        for event_type in event_types:
            if callback in self._connected_callbacks[event_type]:
                self._connected_callbacks[event_type].remove(callback)
