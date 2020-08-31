import os
import logging
from logging.handlers import TimedRotatingFileHandler


def get_logger(thread_name='main', file='logs/', level=20):
    logger = logging.getLogger(thread_name)
    logger.setLevel(level)

    file_handler = TimedRotatingFileHandler(os.path.join(file, thread_name + '.log'), when='midnight')
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger



