

import logging
import os


"""
Logging for Gimpfu

Only used by top.py
Other modules import logging and do like:
logger = logging.getLogger("GimpFu.MarshalPDB")

See 'Using logging in multiple modules'
recipe https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook
"""

class FuLogger:

    @staticmethod
    def getGimpFuLogger():
        """ Initialize and return the root logger for GimpFu. """

        logger = logging.getLogger('GimpFu')

        # possible levels are DEBUG, INFO, WARNING, ERROR, CRITICAL
        # Some sub loggers setLevel separately, and must be enabled by code changes
        # E.G. GimpTypes module is voluminous and does its own setLevel
        if os.getenv("GIMPFU_DEBUG") is not None:
            logger.setLevel(logging.DEBUG)  # Show every log message
        else:
            logger.setLevel(logging.WARNING)   # Omit DEBUG and INFO

        """
        A logger contains one or more handlers,
        components which serialize e.g. print the logged stream of messages.
        I.E. the stream can be forked to console AND a file.
        The handlers can have a level more restrictive than the logger.
        """
        # create file handler which logs even debug messages
        #fh = logging.FileHandler('spam.log')
        #fh.setLevel(logging.DEBUG)
        # create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        # -20 means column padded to 20 chars
        formatter = logging.Formatter('%(name)-23s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        #fh.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(ch)
        #logger.addHandler(fh)

        return logger
