import os
import logging


class Config(object):

    _current_dir_path = os.path.dirname(os.path.realpath(__file__))

    resources_path = '{}/resources'.format(_current_dir_path)

    books_path = '{}/books'.format(resources_path)

    logging_level = logging.INFO


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    level=Config.logging_level)
