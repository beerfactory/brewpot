import logging
import time

import brewpot.core.engine as engine
from brewpot.core.engine import EngineStartedEvent
from brewpot.core.events import AnyEvent


logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m-%d %H:%M:%S',
)
logger = logging.getLogger('brewpot-main')


def callback(event):
    logger.info("event received %s", str(type(event)))
    time.sleep(1)


if __name__ == '__main__':
    logger.info("starting")
    eng = engine.newEngine(dict())
    eng.register_event_callback(eng.context, callback, [EngineStartedEvent, AnyEvent])
    eng.start()
