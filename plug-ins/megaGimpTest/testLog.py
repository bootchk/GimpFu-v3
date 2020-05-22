


"""
Logging for megaTestGimp
"""



import logging

# logger for this plugin.  GimpFu has its own logger
logger = logging.getLogger('megaGimpTest')

# TODO make the level come from the command line or the environment
logger.setLevel(logging.INFO)
#logger.setLevel(logging.WARNING)

# create file handler which logs even debug messages
#fh = logging.FileHandler('spam.log')
#fh.setLevel(logging.DEBUG)
# create console handler with same log level
ch = logging.StreamHandler()
# possible levels are DEBUG, INFO, WARNING, ERROR, CRITICAL
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
#fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
#logger.addHandler(fh)
logger.addHandler(ch)




class TestLog:

    '''
    '''

    logSummary = []

    @classmethod
    def say(cls, message):
        ''' '''

        TestLog.logSummary.append(message)

        # interspersed in standard log (usually console)
        logger.info(message)

        ''' wrapper of warnings.warn() that fixpoints the parameters. '''
        # stacklevel=2 means print two lines, including caller's info
        #warnings.warn(message, DeprecationWarning, stacklevel=2)


    @classmethod
    def summarize(cls):
        if not TestLog.logSummary:
            result = False
        else:
            print("=================================")
            print("MegaTest summary.")
            print("=================================")
            for line in TestLog.logSummary:
                print(line)
            print("")
            result = True
        return result
