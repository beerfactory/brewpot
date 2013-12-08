from core import framework
import logging

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m-%d %H:%M:%S',
)
logger = logging.getLogger('brewpot')

if __name__ == '__main__':
    logger.info("starting")
    fwk = framework.newFramework(dict())
    fwk.start()
