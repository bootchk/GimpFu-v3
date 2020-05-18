
'''
OLD

import sys

# Insure all warnings (deprecation and user) will be printed
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("default") # Change the filter in this process

def warn(message):
    """ Warn using the python warnings module

    Which is not very apropos, warning is about GimpFu constructs is Author's source ,
    not usually about Python per se.
    """
    # stacklevel=2 means print two lines, including caller's info
    warnings.warn(message, DeprecationWarning, stacklevel=2)
'''



import logging


class Deprecation():
    '''
    Knows how to tell Author about deprecations.

    Accumulates warnings into a summary.

    Many occur at registration time.

    Best to print summary at run-time als.
    TODO are the registration-time deprecations summarized at run time

    FUTURE set procedure name in state, to be prepended to messages
    FUTURE print the Author's source.
    '''

    log = []

    logger = logging.getLogger("GimpFu.Deprecation")

    @classmethod
    def say(cls, message):
        ''' Tell user about a deprecation '''

        Deprecation.log.append(message)

        Deprecation.logger.warning(message)



    @classmethod
    def summarize(cls):
        if not Deprecation.log:
            result = False
        else:
            print("=================================")
            print("GimpFu's summary of deprecations.")
            print("=================================")
            for line in Deprecation.log:
                print(line)
            print("")
            result = True
        return result
