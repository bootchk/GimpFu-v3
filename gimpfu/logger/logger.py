

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

        # possible levels are DEBUG, INFO, WARNING, ERROR, CRITICAL
        # TODO make the level come from the command line or the environment
        # TODO for now, uncomment one of the following two lines
        #logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.WARNING)

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
