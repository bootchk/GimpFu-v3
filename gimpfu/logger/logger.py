

import logging


"""
Logging for Gimpfu

Only used by gimpfu_top.
Other modules import logging and do like:
logger = logging.getLogger("GimpFu.MarshalPDB")

See 'Using logging in multiple modules'
recipe https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook
"""

class FuLogger:

    @staticmethod
    def get_logger():
        """ Initialize and return the root logger for GimpFu. """

        logger = logging.getLogger('GimpFu')

        # TODO make the level come from the command line or the environment
        #logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.WARNING)

        # create file handler which logs even debug messages
        #fh = logging.FileHandler('spam.log')
        #fh.setLevel(logging.DEBUG)
        # create console handler with same log level
        ch = logging.StreamHandler()
        # possible levels are DEBUG, INFO, WARNING, ERROR, CRITICAL
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        #fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        #logger.addHandler(fh)
        logger.addHandler(ch)

        return logger
