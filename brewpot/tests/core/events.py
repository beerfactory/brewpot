import unittest

from brewpot.core import base as framework

from brewpot.core.events import *


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
