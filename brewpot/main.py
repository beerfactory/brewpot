from brewpot.core.engine import base as engine
from brewpot.core.engine.events import EngineStartedEvent
from brewpot.core.events import AnyEvent
import logging
import time

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m-%d %H:%M:%S',
)
logger = logging.getLogger('brewpot')


def callback(event):
    logger.info("event received %s", str(type(event)))
    time.sleep(1)


if __name__ == '__main__':
    logger.info("starting")
    eng = engine.newEngine(dict())
#    fwk.register_event_callback(fwk.get_context(), callback, [FrameworkStartedEvent, AnyEvent])
    eng.start()
    eng.stop()
