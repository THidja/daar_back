import logging


class Config(object):
    logging_level = logging.WARNING


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    level=Config.logging_level)