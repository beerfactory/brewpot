import unittest
from brewpot.core.events import *
from brewpot.core.engine import base as framework


class EventDispatcherTest(unittest.TestCase):

    def test_sendEvent1(self):
        self.event = False

        def callback(self):
            self.event = True

        dispatcher = EventDispatcher(framework.newEngine(dict()))
        dispatcher.register(callback, [Event])
        dispatcher.send(Event())


if __name__ == '__main__':
    unittest.main()
