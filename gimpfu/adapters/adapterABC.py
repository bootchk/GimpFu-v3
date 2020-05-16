
from abc import ABC, abstractmethod


# !!!! NOT USED.  Instead, Adapter defines a base implementation of DynamicWriteableAdaptedProperties etc.
# So this is cruft, in case we find a reason for it.


"""
Abstract Base Class for Adapter and subclasses thereof.

Enforces that an instance of Adapter must override DynamicWriteableAdaptedProperties, etc.
"""
class AdapterABC(ABC):

    """
    This declares the method as abstract: must be overridden.
    The implementation here can be accessed from a subclass using super.
    The implementation says that the "default" is that the subclass has NO adapted properties.
    """
    @classmethod
    @abstractmethod
    def DynamicWriteableAdaptedProperties(cls):
        return ()
