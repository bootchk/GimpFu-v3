

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp

from adaption.generic_value import FuGenericValue
from message.proceed_error import *

import logging


# TODO not a pure class, but with instances
# __init__,   dump() => __repr__
# and rename methods push_gvalue => push()
# and with method get_empty_of_length(length)

class FuValueArray():
    '''
    Adapts GimpValueArray.

    Responsibilities:

    - Keeps a list, and produces a GimpValueArray.
    Provides stack ops for the list.
    - Convenience methods for getting empty GimpValueArray

    A GimpValueArray holds arguments.
    Arguments are not one-to-one with items in GimpValueArray because:
    1.) Gimp's (int, [float]) pair of formal arguments
        is mangled by PyGObject to one GValue, a GArray.
        Thus a v2 Author's (int, [float]) is mangled by GimpFu to one GValue.
    2.) GimpFu inserts RunMode arguments not present in Author's args

                       FuValueArray  GimpValueArray
    -----------------------------------------
    indexable          Y             Y
    static len         N             Y
    stack push/pop ops Y             N

    A singleton, with static methods and data

    In a push operations, the gtype may be from the value,
    or the gtype may be passed (when an upcast occurred previously.)
    '''

    logger = logging.getLogger("GimpFu.FuValueArray")

    # class var for the FuValueArray singleton:   _list_gvalues

    @classmethod
    def len(cls):
        return len(cls._list_gvalues)


    @classmethod
    def dump(cls):
        ''' Not a true repr, more akin to str '''
        result = f"Length: {cls.len()} :" + ', '.join(str(item) for item in cls._list_gvalues)
        return result


    @classmethod
    def reset(cls):
        cls._list_gvalues = []


    @classmethod
    def push_gvalue(cls, a_gvalue):
        ''' Push a Gvalue. '''
        cls._list_gvalues.append(a_gvalue)


    @classmethod
    def get_gvalue_array(cls):
        ''' Return a GimpValueArray for the elements in the singleton instance. '''
        result = Gimp.ValueArray.new(cls.len())

        # non-pythonic iteration over ValueArray
        index = 0
        for item in cls._list_gvalues:
            result.insert(index, item)
            index += 1
        return result


    @classmethod
    def _fill_with_nonce(cls, array, length):
        """ Fill the array with don't care GValues. """
        for i in range(0, length) :
            # value_array.append(None)    generates TypeError: unknown type (null) later???
            # Although docs say this creates an uninitialized GValue

            gen_value = FuGenericValue.new_int_gvalue()
            array.append(gen_value)


    @classmethod
    def get_empty_gvalue_array(cls, length):
        """ Return an empty ValueArray.

        Having unspecified/don't care GValues in it.
        """
        # !!! pre-allocated length, but will have length 0
        result = Gimp.ValueArray.new(length)

        cls._fill_with_nonce(result, length)

        FuValueArray.logger.debug(f"get_empty_gvalue_array of length: {length}")
        # ensure result length
        assert result.length() == length
        return result

    '''
    CRUFT

    def _get_empty_value_array(self):
        """ Return a Gimp.ValueArray of same length as self.
        Each element in ValueArray will be of type int, with don't care value.
        """
        assert self._length > 0
        # pass length as prealloc
        value_array = Gimp.ValueArray.new(self._length)
        # a new GimpValueArray always has length 0
        assert value_array.length() == 0

        for i in range(0, self._length) :
            # This generates TypeError: unknown type (null) later???
            # Although docs say this creates an uninitialized GValue
            # value_array.append(None)
            gen_value = FuGenericValue.new_int_gvalue()
            value_array.append(gen_value)
        assert value_array.length() == self._length
        return value_array
    '''
