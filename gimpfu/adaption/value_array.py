

import gi

# gi.require_version("GLib", "2.32")
from gi.repository import GLib    # GArray

from gi.repository import GObject    # GObject type constants

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp




from message.proceed_error import *




class FuValueArray():
    '''
    Adapts GimpValueArray.

    Keeps a list, and produces a GimpValueArray.
    Provides stack ops for the list.

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
    def push_value(cls, value):
        ''' Push a Gvalue where gtype can be gotten from the value. '''
        a_gvalue = FuValueArray.new_gvalue( value.__gtype__, value)
        cls._list_gvalues.append(a_gvalue)

    @classmethod
    def push_type_value_pair(cls, go_arg_type, go_arg):
        ''' Push a Gvalue given (gtype, value). '''
        a_gvalue = FuValueArray.new_gvalue( go_arg_type, go_arg)
        cls._list_gvalues.append(a_gvalue)


    @classmethod
    def get_gvalue_array(cls):
        ''' Return a GimpValueArray for the elements in the list. '''
        result = Gimp.ValueArray.new(cls.len())

        # non-pythonic iteration over ValueArray
        index = 0
        for item in cls._list_gvalues:
            result.insert(index, item)
            index += 1
        return result


    '''
    !!! Can't assign GValue to python object: foo = GObject.Value(Gimp.Image, x) ???
    Must pass directly to Gimp.ValueArray.insert() ???

    ??? I don't understand why GObject.Value() doesn't determine the type of its second argument
    I suppose GObject.Value() can't know all the types, is generic.
    '''
    @staticmethod
    def new_gvalue(gvalue_type, value):
        ''' Returns GValue'''
        # assert gvalue_type is a GObject type constant like GObject.TYPE_STRING
        '''
        An exception is usually not caused by plugin author, usually GimpFu programming error.
        Usually "Must be a GObject.GType, not a type"
        '''
        try:
            result = GObject.Value(gvalue_type, value)
        except Exception as err:
            do_proceed_error(f"Creating GValue for type: {gvalue_type}, value: {value}, err: {err}")
            # Return some bogus value so can proceed
            result = GObject.Value( GObject.TYPE_INT, 1 )
            # TODO would this work??
            # result = GObject.Value( GObject.TYPE_NONE, None )
        return result
