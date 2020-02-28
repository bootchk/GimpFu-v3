

import gi

# gi.require_version("GLib", "2.32")
from gi.repository import GLib    # GArray

from gi.repository import GObject    # GObject type constants

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp




from message.proceed_error import *




class FuValueArray():
    '''
    Adapter of GimpValueArray.

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









    # cruft follows



    """
    TODO gimp_param_array
    @staticmethod
    def new_gimp_float_array(float_list):
        '''
        '''
        value_array = Gimp.FloatArray.new(len(float_list))
        index = 0
        for x in float_list:
            gvalue = FuValueArray.new_gvalue(GObject.TYPE_FLOAT, x)
            value_array.insert(index, gvalue)
            index += 1

        return value_array
    """

    '''
    !!! GArray is not mentioned in some older GObject documents, only GValueArray
    '''
    @staticmethod
    def new_g_array_of_float(float_list):
        ''' '''
        length = len(float_list)
        # size of each element: enough to hold a g_double
        # Not GObject.GArray
        g_array = GLib.GArray.new( True, True, )  # optimize: sized_new()
        for x in float_list:
            #gvalue = FuValueArray.new_gvalue(GObject.TYPE_FLOAT, x)
            g_array.append_val(x)
        print("new_g_array_of_float returns:", g_array)
        return g_array


    '''
    Just cast, hope that GI converts it?

    '''
    @staticmethod
    def new_gimp_float_array(float_list):
        ''' Returns instance of Gimp.FloatArray initialized from a Python list of float '''

        # return float_list, Gimp.FloatArray
        # error: expect Boxed

        #return float_list, Gimp.GimpFloatArray
        # Failed to create Gimp.FloatArray: 'gi.repository.Gimp' object has no attribute 'GimpFloatArray'.

        return float_list, Gimp.FloatArray.__gtype__
        # >>>>GimpFu continued past error: Creating GValue for type: <GType GimpFloatArray (19639968)>, value: [1536.0, 0.0, 1536.0, 1984.0], err: Expected Boxed


    """
    @staticmethod
    def new_gimp_float_array(float_list):
        ''' Returns instance of Gimp.FloatArray initialized from a Python list of float '''

        #This not work, there is no constructor for Gimp.FloatArray
        #value_array = Gimp.FloatArray(len(float_list))

        # This not work:
        # Just return the list and cast it, hope that PyGObject really treats lists as Arrays
        # return float_list

        g_array = FuValueArray.new_g_array_of_float(float_list)

        gimp_float_array = Gimp.FloatArray.copy(g_array)
        print("new_gimp_float_array returns:", gimp_float_array)
        return gimp_float_array
    """
