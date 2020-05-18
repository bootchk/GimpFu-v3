

import logging

"""
Singleton class for logging from Adapter instances.

Defines a single attribute 'logger' in the GimpFu tree of loggers

It is problematic to make each instance of Adapter or subclass thereof have its own logger.
Adapter instance attributes such as 'logger' are hard because of the __setattr__ recursion.
"""

class AdapterLogger:

    logger = logging.getLogger("GimpFu.Adaptor")
